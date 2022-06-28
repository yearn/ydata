import argparse
import gc
import logging
import os
import signal
import sys
from decimal import Decimal
from typing import Any, Literal, Optional, Type, Union, cast

from dotenv import load_dotenv
from gql.transport.exceptions import TransportError
from sqlmodel import Session, SQLModel, col, create_engine, select

from src.constants import BLOCK_SIZE, LONDON_DAY_BLOCK, MAX_UINT256, ZERO_ADDRESS
from src.graphql.queries.vault_transfers import vault_transfers_query
from src.models import Vault, VaultDeposit, VaultWithdrawal, create_id
from src.networks import Network
from src.utils.magic import get_price
from src.utils.network import rate_limit, retry
from src.utils.web3 import Web3Provider
from src.yearn import Subgraph
from src.yearn import Vault as TVault
from src.yearn import Yearn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

# create database engine
engine = create_engine(os.environ["DATABASE_URI"])
SQLModel.metadata.create_all(engine)


def handle_signal(*args: Any) -> None:
    logger.error("Interrupted by user")
    sys.exit()


@rate_limit(max_calls_per_window=1, call_window=30)
@retry(retries=0)
def __commit_vault_transfers_by_web3(
    transfer_type: Literal["withdrawals", "deposits"],
    vault: TVault,
    w3: Web3Provider,
) -> None:
    with Session(engine) as session:
        vault_token_decimal = Decimal(10**vault.token.decimals)
        vault_row, vault_transfer_row, vault_transfer = get_last_vault_transfer(
            transfer_type, vault, session
        )
        if vault_row is None:
            return

        start_block = LONDON_DAY_BLOCK
        if vault_transfer_row:
            start_block = vault_transfer_row.block_number + 1
        current_block = max(w3.provider.eth.get_block("latest")["number"], start_block)
        blocks = range(start_block, current_block, BLOCK_SIZE)

        transfer_address = "sender" if transfer_type == "withdrawals" else "receiver"
        burn_or_mint_address = (
            "receiver" if transfer_type == "withdrawals" else "sender"
        )
        for from_block in blocks:
            to_block = from_block + BLOCK_SIZE
            events = w3.fetch_events(vault.address, "Transfer", from_block, to_block)

            transfers = [
                event
                for event in events
                if event["args"][burn_or_mint_address] == ZERO_ADDRESS
            ]
            for transfer in transfers:
                address = transfer["args"][transfer_address]
                block_number = transfer["blockNumber"]
                tx_hash = transfer["transactionHash"].hex()
                share_amount_decimal = float(
                    Decimal(transfer["args"]["value"]) / vault_token_decimal
                )
                share_price = get_price(vault_row.token_address, block_number)

                vault_withdrawal = vault_transfer(
                    id=create_id(
                        f'{block_number}_{tx_hash}',
                        vault_row.network,
                    ),
                    network=vault_row.network,
                    block_number=block_number,
                    timestamp=w3.provider.eth.get_block(block_number)["timestamp"],
                    transaction_hash=tx_hash,
                    transfer_address=address,
                    shares=share_amount_decimal,
                    share_price=share_price,
                    vault_id=vault_row.id,
                )
                session.add(vault_withdrawal)
                session.commit()


def get_last_vault_transfer(
    transfer_type: Literal["withdrawals", "deposits"], vault: TVault, session: Session
) -> tuple[
    Optional[Vault],
    Optional[Union[VaultWithdrawal, VaultDeposit]],
    Union[Type[VaultWithdrawal], Type[VaultDeposit]],
]:
    vault_transfer: Union[Type[VaultWithdrawal], Type[VaultDeposit]] = (
        VaultWithdrawal if transfer_type == "withdrawals" else VaultDeposit
    )
    # get current vault from db that is bound to the same session
    vault_row_id = create_id(vault.address, vault.network)
    vault_row: Vault = cast(Vault, session.get(Vault, vault_row_id))

    if vault_row is None:
        return None, None, None

    # retrieve current vault's last transfer
    statement = (
        select(vault_transfer)
        .where(vault_transfer.vault_id == vault_row.id)
        .order_by(col(vault_transfer.id).desc())
        .limit(1)
    )
    vault_transfer_row = cast(
        Optional[Union[VaultWithdrawal, VaultDeposit]], session.exec(statement).first()
    )
    return vault_row, vault_transfer_row, vault_transfer


@rate_limit(max_calls_per_window=1, call_window=30)
@retry(
    retries=0,
    exception=TransportError,
    exception_handler=lambda transfer_type, vault, subgraph: f"Failed to fetch subgraph data from vault {vault.name}",
)
def __commit_vault_transfers_by_subgraph(
    transfer_type: Literal["withdrawals", "deposits"],
    vault: TVault,
    subgraph: Subgraph,
) -> None:
    with Session(engine) as session:
        vault_token_decimal = Decimal(10**vault.token.decimals)
        vault_row, vault_transfer_row, vault_transfer = get_last_vault_transfer(
            transfer_type, vault, session
        )
        if vault_row is None:
            return

        skip_id = ""
        if vault_transfer_row:
            # slice to remove network portion
            skip_id = vault_transfer_row.id[len(str(vault_row.network)) + 1 :]

        while True:
            (query, shares_minted_or_burnt) = vault_transfers_query(
                transfer_type,
                vault_row.address.lower(),
                1000,
                skip_id,
                LONDON_DAY_BLOCK,
            )
            response = subgraph.client.execute(query)
            transfers = response.get(transfer_type, [])
            if len(transfers) == 0:
                break

            for transfer in transfers:
                block_number = transfer["blockNumber"]
                share_amount = transfer[shares_minted_or_burnt]
                if share_amount == MAX_UINT256:
                    continue
                share_amount_decimal = float(
                    Decimal(share_amount) / vault_token_decimal
                )
                share_price = get_price(vault_row.token_address, int(block_number))
                vault_withdrawal = vault_transfer(
                    id=create_id(transfer["id"], vault_row.network),
                    network=vault_row.network,
                    block_number=block_number,
                    timestamp=transfer["timestamp"],
                    transaction_hash=transfer["transaction"]["id"],
                    transfer_address=transfer["account"]["id"],
                    shares=share_amount_decimal,
                    share_price=share_price,
                    vault_id=vault_row.id,
                )
                session.add(vault_withdrawal)
                session.commit()
            skip_id = transfers[-1]["id"]


@retry(retries=0)
def __do_commits(yearn: Yearn, subgraph: Subgraph, w3: Web3Provider) -> None:
    # refresh data
    logger.info(f"Refreshing data for network {yearn.network}")
    yearn.refresh()

    for vault in yearn.vaults:
        # garbage collection to save memory usage
        gc.collect()

        logger.info(
            f"Updating transfers for vault {vault.name} on {vault.network.name}"
        )
        # vault transfer data
        if vault.network == Network.Mainnet:
            __commit_vault_transfers_by_subgraph("withdrawals", vault, subgraph)
            __commit_vault_transfers_by_subgraph("deposits", vault, subgraph)
        else:
            __commit_vault_transfers_by_web3("withdrawals", vault, w3)
            __commit_vault_transfers_by_web3("deposits", vault, w3)


def main(network: Network) -> None:
    # handle signals
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # initialize instances
    yearn = Yearn(network)
    subgraph = Subgraph(network)
    w3 = Web3Provider(network)

    # main loop
    logger.info("Entering main loop")
    while True:
        # garbage collection to save memory usage
        gc.collect()

        __do_commits(yearn, subgraph, w3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--network", type=int, required=True, help="the blockchain to connect to"
    )
    args = parser.parse_args()
    main(Network(args.network))
