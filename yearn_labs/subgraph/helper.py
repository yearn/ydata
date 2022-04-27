from typing import Union, TypedDict, Optional, List
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from ..vault import Vault
from ..strategy import Strategy
from .queries import query_all_vaults, query_vault_by_address
from .queries import query_all_strategies, query_strategy_by_address
from .responses import parse_strategies, parse_vaults


class StrategyContext(TypedDict, total=False):
    address: Union[str, List[str]]
    nameLike: Union[str, List[str]]
    groupId: Union[str, List[str]]
    vaultAddress: Union[str, List[str]]
    vaultName: Union[str, List[str]]


class VaultContext(TypedDict, total=False):
    address: Union[str, List[str]]
    nameLike: Union[str, List[str]]


class SubgraphHelper:
    """
    Helper class for querying data hosted in the Yearn Subgraph
    """

    def __init__(self, url: str):
        transport = RequestsHTTPTransport(url=url)
        self.client = Client(transport=transport)

    def get_vaults(
        self, context: Optional[VaultContext] = {}
    ) -> List[Union[Vault, None]]:
        # filter by vault address
        if "address" in context:
            addresses = context["address"]
            if not isinstance(addresses, List):
                addresses = [addresses]
            queries = [query_vault_by_address(address) for address in addresses]
            vaults = set(
                [
                    vault
                    for q in queries
                    for vault in parse_vaults(self.client.execute(q))
                ]
            )

        # fetch all vaults
        else:
            query = query_all_vaults()
            vaults = set(parse_vaults(self.client.execute(query)))

        # filter by vault name
        if "nameLike" in context:
            names = context["nameLike"]
            if not isinstance(names, List):
                names = [names]
            vaults = set(
                filter(
                    lambda v: any(name.lower() in v.name.lower() for name in names),
                    vaults,
                )
            )
        return vaults

    def get_strategies(self, context: Optional[StrategyContext] = {}) -> List[Strategy]:
        # filter by strategy address
        if "address" in context:
            addresses = context["address"]
            if not isinstance(addresses, List):
                addresses = [addresses]
            queries = [query_strategy_by_address(address) for address in addresses]
            strategies = set(
                [
                    strat
                    for q in queries
                    for strat in parse_strategies(self.client.execute(q))
                ]
            )

        # filter by vault address
        elif "vaultAddress" in context:
            vaults = self.get_vaults({"address": context["vaultAddress"]})
            strategies = set([strat for vault in vaults for strat in vault.strategies])

        # filter by vault name
        elif "vaultName" in context:
            vaults = self.get_vaults({"nameLike": context["vaultName"]})
            strategies = set([strat for vault in vaults for strat in vault.strategies])

        # fetch all strategies
        else:
            query = query_all_strategies()
            strategies = set(parse_strategies(self.client.execute(query)))

        # filter by strategy name
        if "nameLike" in context:
            names = context["nameLike"]
            if not isinstance(names, List):
                names = [names]
            strategies = set(
                filter(
                    lambda s: any(name.lower() in s.name.lower() for name in names),
                    strategies,
                )
            )
        return strategies
