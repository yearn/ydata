import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, List, Literal, Union

from gql import Client, gql
from gql.transport.exceptions import TransportError
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as requests_logger

from src.constants import MAX_BLOCK, MAX_UINT256
from src.utils.network import retry
from src.yearn.networks import Network

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
            endpoint = "https://api.thegraph.com/subgraphs/name/rareweasel/yearn-vaults-v2-subgraph-mainnet"
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
        query = gql(
            f"""
        {{
            accountVaultPositions(first: {num_accounts},
                where:{{vault:"{vault.address.lower()}"}},
                orderBy: balanceShares,
                orderDirection: desc) {{
                id
                balanceShares
                account {{
                id
                }}
            }}
        }}
        """
        )
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

    def transfers(
        self,
        transfer_type: Literal["withdrawals", "deposits"],
        vault: "Vault",
        query_len: int = 1000,
        from_block: Union[int, Literal["first"]] = "first",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> Transfers:
        """
        Get all deposits/withdrawals for a vault within a period of time
        """
        from_block = 0 if from_block == "first" else from_block
        to_block = MAX_BLOCK if to_block == "latest" else to_block
        shares_minted_or_burnt = (
            "sharesBurnt" if transfer_type == "withdrawals" else "sharesMinted"
        )

        skip_id: str = ""
        count: int = 0
        shares: float = 0
        account_transfers: dict[str, AccountTransfers] = {}

        vault_token_decimal = Decimal(10**vault.token.decimals)

        while True:
            query = gql(
                f"""
            {{
                {transfer_type}(first: {query_len},
                    where: {{
                        id_gt: "{skip_id}",
                        vault: "{vault.address.lower()}",
                        blockNumber_gte: {from_block},
                        blockNumber_lte: {to_block}
                    }}) {{
                    id
                    account {{
                        id
                    }}
                    {shares_minted_or_burnt}
                }}
            }}
            """
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
