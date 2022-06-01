import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, List

from gql import Client, gql
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import RequestsHTTPTransport

from src.yearn.networks import Network

if TYPE_CHECKING:
    from src.yearn.vaults import Vault

logger = logging.getLogger(__name__)


@dataclass
class WalletBalance:
    address: str
    balanceShares: Decimal


class SubgraphClient:
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
        transport = RequestsHTTPTransport(url=endpoint)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def top_wallets(
        self, vault: "Vault", num_accounts: int = 10
    ) -> List[WalletBalance]:
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
        try:
            response = self.client.execute(query)
        except TransportQueryError:
            return wallets

        for wallet in response.get('accountVaultPositions', []):
            wallets.append(
                WalletBalance(wallet['account']['id'], Decimal(wallet['balanceShares']))
            )
        return wallets
