import logging
from dataclasses import dataclass
from typing import Dict, List, Literal, Set, TypedDict, Union

from src.constants import META_ENDPOINT, YEARN_V1_API_ENDPOINT
from src.utils.network import client, parse_json
from src.yearn.networks import Network
from src.yearn.protocols import Protocol, get_protocol
from src.yearn.strategies import Strategy
from src.yearn.vaults import Token, Vault

logger = logging.getLogger(__name__)


@dataclass
class TokenData:
    name: str
    symbol: str
    address: str
    decimals: int
    display_name: str
    icon: str


@dataclass
class StrategyData:
    name: str
    address: str


@dataclass
class VaultData:
    inception: str
    address: str
    symbol: str
    name: str
    display_name: str
    icon: str
    token: TokenData
    tvl: Dict
    apy: Dict
    strategies: StrategyData
    endorsed: bool
    version: str
    decimals: int
    type: str
    emergency_shutdown: bool
    updated: str
    migration: Union[str, None]
    special: bool


@dataclass
class LocalizedData:
    name: str
    description: str


@dataclass
class Localization:
    en: LocalizedData
    fr: LocalizedData
    es: LocalizedData
    de: LocalizedData
    pt: LocalizedData
    el: LocalizedData
    tr: LocalizedData
    vi: LocalizedData
    zh: LocalizedData
    hi: LocalizedData
    ja: LocalizedData
    id: LocalizedData
    ru: LocalizedData


StrategyMeta = TypedDict(
    "StrategyMeta",
    {
        "$schema": Literal["strategy"],
        "name": str,
        "description": str,
        "addresses": List[str],
        "protocols": List[str],
        "localization": Localization,
    },
)


class Yearn:
    network: Network
    endpoint: str
    _vaults: Set[Vault]
    _strategies: Set[Strategy]

    """
    Interface for providing information about our products
    """

    def __init__(self, network: Network):
        self.network = network
        self.refresh()

    def fetch_vaults(self) -> Union[List[VaultData], Dict]:
        # fetch data from api
        url = YEARN_V1_API_ENDPOINT + f"/{self.network}/vaults/all"
        response = client('get', url)
        jsoned = parse_json(response)
        if jsoned is None:
            logger.error(f"Failed to load vaults for {self.network.name}")
            return {}
        return jsoned

    def fetch_strategy_metadata(self) -> Union[List[StrategyMeta], Dict]:
        # fetch strategy metadata
        url = META_ENDPOINT + f"/strategies/{self.network}/all"
        response = client('get', url)
        jsoned = parse_json(response)
        if jsoned is None:
            logger.error(f"Failed to load metadata for {self.network.name}")
            return {}
        return jsoned

    def map_strategy_protocols(self) -> Dict[str, Set[Protocol]]:
        # map strategy protocols
        protocol_map: Dict[str, Set[Protocol]] = {}
        for strategy in self.fetch_strategy_metadata():
            protocols = set({})
            for protocol_name in strategy["protocols"]:
                protocol = get_protocol(protocol_name)
                if protocol is not None:
                    protocols.add(protocol)
            for address in strategy["addresses"]:
                protocol_map[address] = protocols
        return protocol_map

    def refresh(self):
        protocol_map = self.map_strategy_protocols()
        self._vaults = set({})
        self._strategies = set({})
        for vault in self.fetch_vaults():
            if vault["type"] != "v2":  # get only the V2 vaults
                continue

            _token = vault["token"]
            token = Token(
                address=_token["address"],
                decimals=_token["decimals"],
                name=_token["name"],
                symbol=_token["display_name"],
            )

            strategies = []
            for _strategy in vault["strategies"]:
                strategy = Strategy(
                    network=self.network,
                    address=_strategy["address"],
                    name=_strategy["name"],
                )
                if _strategy["address"] in protocol_map:
                    strategy.protocols = protocol_map[_strategy["address"]]
                strategies.append(strategy)

            self._vaults.add(
                Vault(
                    network=self.network,
                    address=vault["address"],
                    name=vault["name"],
                    token=token,
                    inception=vault["inception"],
                    strategies=strategies,
                )
            )
            self._strategies.update(strategies)

    @property
    def vaults(self) -> List[Vault]:
        return list(self._vaults)

    @property
    def strategies(self) -> List[Strategy]:
        return list(self._strategies)
