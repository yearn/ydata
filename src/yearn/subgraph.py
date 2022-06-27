import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, List, Literal, Union

from gql import Client, gql
from gql.transport.exceptions import TransportError
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as requests_logger

from src.constants import MAX_BLOCK, MAX_UINT256
from src.graphql.queries.account_vault_positions import account_vault_positions_query
from src.graphql.queries.vault_transfers import vault_transfers_query
from src.networks import Network
from src.utils.network import retry

if TYPE_CHECKING:
    from src.yearn.vaults import Vault

requests_logger.setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class WalletBalance:
    address: str
    balanceShares: Decimal


@dataclass
class AccountTransfers:
    count: int
    shares: float


@dataclass
class Transfers:
    count: int
    shares: float
    account_transfers: dict[str, AccountTransfers]


class Subgraph:
    chain_id: Network
    client: Client

    """
    Interface for fetching data from the subgraphs of Yearn
    """

    def __init__(self, network: Network):
        self.chain_id = network
        if network == Network.Mainnet:
            endpoint = "https://api.thegraph.com/subgraphs/name/rareweasel/yearn-vaults-v2-mainnet"
        elif network == Network.Fantom:
            endpoint = (
                "https://api.thegraph.com/subgraphs/name/yearn/yearn-vaults-v2-fantom"
            )
        elif network == Network.Arbitrum:
            endpoint = (
                "https://api.thegraph.com/subgraphs/name/yearn/yearn-vaults-v2-arbitrum"
            )
        transport = RequestsHTTPTransport(url=endpoint)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    @retry(
        exception=TransportError,
        exception_handler=lambda self, vault, num_accounts: f"Failed to fetch contract for {vault.name}",
    )
    def top_wallets(
        self, vault: "Vault", num_accounts: int = 10
    ) -> Union[List[WalletBalance], None]:
        query = account_vault_positions_query(vault.address.lower(), num_accounts)
        wallets: List[WalletBalance] = []
        response = self.client.execute(query)
        for wallet in response.get('accountVaultPositions', []):
            wallets.append(
                WalletBalance(
                    wallet['account']['id'],
                    Decimal(wallet['balanceShares'])
                    / Decimal(10**vault.token.decimals),
                )
            )
        return wallets

    @retry(
        exception=TransportError,
        exception_handler=lambda self, transfer_type, vault, query_len, from_block, to_block: f"Failed to fetch contract for {vault.name}",
    )
    def vault_transfers(
        self,
        transfer_type: Literal["withdrawals", "deposits"],
        vault: "Vault",
        query_len: int = 1000,
        from_block: int = 0,
        to_block: int = MAX_BLOCK,
    ) -> Transfers:
        """
        Get all deposits/withdrawals for a vault within a period of time
        """
        skip_id: str = ""
        count: int = 0
        shares: float = 0
        vault_token_decimal = Decimal(10**vault.token.decimals)
        account_transfers: dict[str, AccountTransfers] = {}

        while True:
            (query, shares_minted_or_burnt) = vault_transfers_query(
                transfer_type,
                vault.address.lower(),
                query_len,
                skip_id,
                from_block,
                to_block,
            )

            response = self.client.execute(query)
            transfers = response.get(transfer_type, [])
            if len(transfers) == 0:
                break

            for transfer in transfers:
                share_amount = transfer[shares_minted_or_burnt]
                if share_amount == MAX_UINT256:
                    continue
                account = transfer["account"]["id"]
                share_amount_decimal = float(
                    Decimal(share_amount) / vault_token_decimal
                )

                count += 1
                shares += share_amount_decimal
                if account_transfers.get(account) is None:
                    account_transfers[account] = AccountTransfers(0, 0)
                account_transfers[account].count += 1
                account_transfers[account].shares += share_amount_decimal

            skip_id = transfers[-1]["id"]

        return Transfers(count, shares, account_transfers)
