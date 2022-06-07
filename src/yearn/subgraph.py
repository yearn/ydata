import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, List, Literal, Union

from gql import Client, gql
from gql.transport.exceptions import TransportError
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as requests_logger

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
class AccountShare:
    count: int
    shares: float


@dataclass
class Transfers:
    count: int
    shares: float
    account_shares: dict[str, AccountShare]


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
        transfer_type: Literal['deposits', 'withdrawals'],
        vault: "Vault",
        query_len: int = 1000,
        from_block: Union[int, Literal["first"]] = "first",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> Transfers:
        """
        Get all deposits/withdrawals for a vault within a period of time
        """
        skip: int = 0
        count: int = 0
        shares: float = 0
        account_shares: dict[str, AccountShare] = {}
        shares_type = "sharesMinted" if transfer_type == "deposits" else "sharesBurnt"

        while True:
            query = gql(
                f"""
            {{
                {transfer_type}(first: {query_len}, skip: {skip},
                    where: {{
                        vault: "{vault.address.lower()}",
                        blockNumber_gte: {from_block},
                        blockNumber_lte: {to_block}
                    }}) {{
                    {shares_type}
                    account {{
                        id
                    }}
                }}
            }}
            """
            )

            response = self.client.execute(query)
            transfers = response.get(transfer_type, [])
            if len(transfers) == 0:
                break

            for transfer in transfers:
                sharesMintedOrBurnt = Decimal(transfer[shares_type]) / Decimal(
                    10**vault.token.decimals
                )
                account = transfer['account']['id']

                count += 1
                shares += sharesMintedOrBurnt
                if account_shares.get(account) is None:
                    account_shares[account] = AccountShare(0, 0)
                account_shares[account].count += 1
                account_shares[account].shares += sharesMintedOrBurnt

            skip += query_len

        return Transfers(count, shares, account_shares)
