import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Union

from gql import Client, gql
from gql.transport.exceptions import TransportError
from gql.transport.requests import RequestsHTTPTransport
from graphql import GraphQLError

from src.utils.network import retry
from src.yearn.networks import Network
from src.yearn.protocols import Protocol, get_protocol

logger = logging.getLogger(__name__)


ProtocolMap: dict[Network, dict[Protocol, str]] = {
    Network.Mainnet: {
        get_protocol(
            'yearn'
        ): "https://api.thegraph.com/subgraphs/name/messari/yearn-v2-ethereum",
        get_protocol(
            'sushi'
        ): "https://api.thegraph.com/subgraphs/name/messari/sushiswap-ethereum",
        get_protocol(
            'maker'
        ): "https://api.thegraph.com/subgraphs/name/messari/makerdao-ethereum",
        get_protocol(
            'cream'
        ): "https://api.thegraph.com/subgraphs/name/messari/cream-finance-ethereum",
        get_protocol(
            'curve'
        ): "https://api.thegraph.com/subgraphs/name/messari/curve-finance-ethereum",
        get_protocol(
            'convex'
        ): "https://api.thegraph.com/subgraphs/name/messari/convex-finance-ethereum",
        get_protocol(
            'uniswap'
        ): "https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-ethereum",
        get_protocol(
            'liquity'
        ): "https://api.thegraph.com/subgraphs/name/messari/liquity-ethereum",
        get_protocol(
            'compound'
        ): "https://api.thegraph.com/subgraphs/name/messari/compound-ethereum",
        get_protocol(
            'balancer'
        ): "https://api.thegraph.com/subgraphs/name/messari/balancer-v2-ethereum",
        get_protocol(
            'aave'
        ): "https://api.thegraph.com/subgraphs/name/messari/aave-v2-ethereum",
    },
    Network.Fantom: {
        get_protocol(
            'curve'
        ): "https://api.thegraph.com/subgraphs/name/messari/curve-finance-fantom",
    },
    Network.Arbitrum: {
        get_protocol(
            'yearn'
        ): "https://api.thegraph.com/subgraphs/name/messari/yearn-v2-arbitrum",
        get_protocol(
            'balancer'
        ): "https://api.thegraph.com/subgraphs/name/messari/balancer-v2-arbitrum",
    },
}


@dataclass
class FinancialsDailySnapshot:
    blockNumber: int
    timestamp: int
    totalValueLockedUSD: Decimal
    dailySupplySideRevenueUSD: Decimal


class Subgraph:
    chain_id: Network
    protocol: Protocol

    """
    Messari's subgraphs for DeFi protocols using a standardized schema
    """

    def __init__(self, network: Network, protocol: Union[str, Protocol]):
        self.chain_id = network
        if isinstance(protocol, str):
            self.protocol = get_protocol(protocol)
        else:
            self.protocol = protocol

        self.client = None
        endpoint = ProtocolMap[self.chain_id].get(self.protocol, None)
        if endpoint is None:
            logger.error(
                f"Failed to initialize Messari subgraph for {self.protocol} on {self.chain_id.name}"
            )
        else:
            transport = RequestsHTTPTransport(url=endpoint)
            self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def __repr__(self):
        return f"<Messari Subgraph network={self.chain_id.name} protocol={self.protocol.name}>"

    @retry(
        exception=TransportError,
        exception_handler=lambda self, from_block, to_block: f"Failed to fetch daily snapshots for {self.protocol}",
    )
    def daily_snapshots(
        self,
        from_block: Union[int, Literal["first"]] = "first",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> list[FinancialsDailySnapshot]:
        if self.client is None:
            return []

        from_block = 0 if from_block == "first" else from_block
        # fetch the most recent update
        if to_block == "latest":
            query = gql(
                f"""
            {{
                financialsDailySnapshots(
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
            if len(response['financialsDailySnapshots']) > 0:
                to_block = int(response['financialsDailySnapshots'][0]['blockNumber'])
            else:
                return []

        # fetch the financial daily snapshots
        snapshots: list[FinancialsDailySnapshot] = []
        try:
            query = gql(
                f"""
            {{
                financialsDailySnapshots(
                    where:{{
                        blockNumber_gte:"{from_block}",
                        blockNumber_lte:"{to_block}",
                    }},
                    orderBy: blockNumber,
                    first: 1000,
                ) {{
                    blockNumber
                    timestamp
                    totalValueLockedUSD
                    dailySupplySideRevenueUSD
                }}
            }}
            """
            )
            key = "dailySupplySideRevenueUSD"
            response = self.client.execute(query)
        except GraphQLError:
            query = gql(
                f"""
            {{
                financialsDailySnapshots(
                    where:{{
                        blockNumber_gte:"{from_block}",
                        blockNumber_lte:"{to_block}",
                    }},
                    orderBy: blockNumber,
                    first: 1000,
                ) {{
                    blockNumber
                    timestamp
                    totalValueLockedUSD
                    supplySideRevenueUSD
                }}
            }}
            """
            )
            key = "supplySideRevenueUSD"
            response = self.client.execute(query)

        blockNumber = 0
        for snapshot in response.get('financialsDailySnapshots', []):
            if int(snapshot['blockNumber']) > blockNumber:
                blockNumber = int(snapshot['blockNumber'])
                snapshots.append(
                    FinancialsDailySnapshot(
                        snapshot['blockNumber'],
                        snapshot['timestamp'],
                        Decimal(snapshot['totalValueLockedUSD']),
                        Decimal(snapshot[key]),
                    )
                )
        if from_block >= to_block:
            return snapshots
        else:
            from_block = blockNumber + 1
            return self.daily_snapshots(from_block, to_block) + snapshots
