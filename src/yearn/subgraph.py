import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, List, Union

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
