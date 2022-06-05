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
class PricePerShare:
    blockNumber: int
    timestamp: int
    pricePerShare: Decimal


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
        exception_handler=lambda self, vault, num_accounts: f"Failed to fetch top wallets for {vault.name}",
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

    @retry(
        exception=TransportError,
        exception_handler=lambda self, vault, from_block, to_block: f"Failed to fetch price per share for {vault.name}",
    )
    def price_per_share(
        self,
        vault: "Vault",
        from_block: Union[int, Literal["first"]] = "first",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> Union[List[PricePerShare], None]:
        from_block = 0 if from_block == "first" else from_block
        # fetch the most recent update
        if to_block == "latest":
            query = gql(
                f"""
            {{
                vaultUpdates(
                    where:{{
                        vault:"{vault.address.lower()}",
                    }},
                    orderBy: blockNumber,
                    orderDirection: desc,
                    first: 1,
                ) {{
                    blockNumber
                }}
            }}
            """
            )
            response = self.client.execute(query)
            if len(response['vaultUpdates']) > 0:
                to_block = int(response['vaultUpdates'][0]['blockNumber'])
            else:
                return []

        # fetch the share prices from vault updates
        query = gql(
            f"""
        {{
            vaultUpdates(
                where:{{
                    vault:"{vault.address.lower()}",
                    blockNumber_gte:"{from_block}",
                    blockNumber_lte:"{to_block}",
                }},
                orderBy: blockNumber,
                first: 1000,
            ) {{
                blockNumber
                timestamp
                pricePerShare
            }}
        }}
        """
        )
        prices: List[PricePerShare] = []
        response = self.client.execute(query)

        blockNumber = 0
        for update in response.get('vaultUpdates', []):
            if int(update['blockNumber']) > blockNumber:
                blockNumber = int(update['blockNumber'])
                pricePerShare = Decimal(update['pricePerShare']) / Decimal(
                    10**vault.token.decimals
                )
                prices.append(
                    PricePerShare(
                        update['blockNumber'],
                        update['timestamp'],
                        pricePerShare,
                    )
                )

        if from_block >= to_block:
            return prices
        else:
            from_block = blockNumber + 1
            return self.price_per_share(vault, from_block, to_block) + prices
