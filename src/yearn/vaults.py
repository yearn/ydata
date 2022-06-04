from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Tuple

from src.yearn.networks import Network
from src.yearn.subgraph import Subgraph

if TYPE_CHECKING:
    from src.yearn.strategies import Strategy


@dataclass
class Token:
    address: str
    decimals: int
    name: str
    symbol: str


@dataclass
class VaultProtocolInfo:
    name: str
    TVLAllocation: float


@dataclass
class VaultTokenInfo:
    name: str
    TVLAllocation: float


@dataclass
class VaultWalletInfo:
    address: str
    TVLAllocation: float


@dataclass
class VaultInfo:
    protocols: List[VaultProtocolInfo]
    tokens: List[VaultTokenInfo]
    topWallets: List[VaultWalletInfo]


class Vault:
    network: Network
    address: str
    name: str
    token: Token
    inception: int
    strategies: List["Strategy"]
    """
    Contains vault-level information
    """

    def __init__(
        self,
        network: Network,
        address: str,
        name: str,
        token: Token,
        inception: int,
        strategies: List["Strategy"],
    ):
        self.network = network
        self.address = address
        self.name = name
        self.token = token
        self.inception = int(inception)
        self.strategies = strategies

        # set vault to self for its strategies
        for strategy in self.strategies:
            strategy.vault = self

    def __repr__(self):
        return f"<Vault name={self.name}>"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    @property
    def wallets(self) -> List[Tuple[str, Decimal]]:
        subgraph = Subgraph(self.network)
        wallets = subgraph.top_wallets(self, num_accounts=10)
        if wallets is None:
            return []
        return [
            (wallet.address, max(Decimal(0), wallet.balanceShares))
            for wallet in wallets
        ]

    def describe(self) -> VaultInfo:
        _protocols: Dict[str, float] = {}
        _tokens: Dict[str, float] = {}
        total_tvl = 0.0
        # TVL distribution of protocols and tokens
        for strategy in self.strategies:
            info = strategy.describe()
            tvl = float(strategy.tvl)
            total_tvl += tvl
            for ptl in info.protocols:
                if ptl in _protocols:
                    _protocols[ptl] += tvl
                else:
                    _protocols[ptl] = tvl
            for tkn in info.tokens:
                if tkn in _tokens:
                    _tokens[tkn] += tvl
                else:
                    _tokens[tkn] = tvl
        if total_tvl > 0:
            _protocols = {k: v / total_tvl for k, v in _protocols.items()}
            _tokens = {k: v / total_tvl for k, v in _tokens.items()}
        protocols = [VaultProtocolInfo(k, v) for k, v in _protocols.items()]
        tokens = [VaultTokenInfo(k, v) for k, v in _tokens.items()]

        # wallet TVL distribution
        wallets = self.wallets
        wallets_tvl = sum([wallet[1] for wallet in wallets])
        wallets = list(sorted(wallets, key=lambda item: item[1], reverse=True)[:10])
        if wallets_tvl > 0.0:
            top_wallets = [
                VaultWalletInfo(wallet[0], float(wallet[1] / wallets_tvl))
                for wallet in wallets
            ]
        else:
            top_wallets = [VaultWalletInfo(wallet[0], 0.0) for wallet in wallets]
        return VaultInfo(protocols, tokens, top_wallets)
