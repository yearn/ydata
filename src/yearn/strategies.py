import time
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Set, Union

from src.yearn.networks import Network, Web3Provider
from src.yearn.protocols import Protocol, get_protocol
from src.yearn.vaults import Vault


@dataclass
class StrategyInfo:
    protocols: List[str]
    tokens: List[str]


class Strategy:
    network: Network
    address: str
    name: str
    vault: Union[Vault, None]
    protocols: Set[Protocol]

    """
    Contains strategy-level information
    """

    def __init__(self, network: Network, address: str, name: str):
        self.network = network
        self.address = address
        self.name = name
        self.vault = None
        self.protocols = set({})

    def __repr__(self):
        return f"<Strategy name={self.name}>"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    @property
    def longevity(self) -> Decimal:
        w3 = Web3Provider(self.network)
        if self.vault is None:
            vault_address = w3.call(self.address, "vault")
        else:
            vault_address = self.vault.address
        params = w3.call(vault_address, "strategies", self.address)
        return Decimal(time.time()) - params[1]  # activation

    @property
    def tvl(self) -> Decimal:
        w3 = Web3Provider(self.network)
        if self.vault is None:
            vault_address = w3.call(self.address, "vault")
            if vault_address is None:
                return Decimal(0.0)
            decimals = Decimal(w3.call(vault_address, "decimals"))
            token_address = w3.call(vault_address, "token")
        else:
            decimals = Decimal(self.vault.token.decimals)
            token_address = self.vault.token.address

        total_assets = w3.call(self.address, "estimatedTotalAssets")
        if total_assets is None:
            return Decimal(0.0)
        total_assets = Decimal(total_assets)
        total_assets /= 10**decimals
        usdc_price = w3.get_usdc_price(token_address)
        return total_assets * usdc_price

    def describe(self) -> StrategyInfo:
        w3 = Web3Provider(self.network)
        addresses = w3.erc20_tokens(self.address)
        tokens = []
        for address in addresses:
            token = w3.get_contract(address)
            if token is not None and hasattr(token.caller, "symbol"):
                tokens.append(token.caller.symbol())

        labels = set(
            [label for address in addresses for label in w3.get_scan_labels(address)]
        )
        for label in labels:
            protocol = get_protocol(label)
            if protocol is not None:
                self.protocols.add(protocol)
        return StrategyInfo(
            [protocol.name for protocol in self.protocols], list(set(tokens))
        )
