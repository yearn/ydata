from typing import TYPE_CHECKING
from typing import List, NamedTuple
from ..risk.scores import VaultRisk

if TYPE_CHECKING:
    from .strategies import Strategy


class Token(NamedTuple):
    address: str
    decimals: int
    name: str
    symbol: str


class Vault:
    address: str
    name: str
    token: Token
    strategies: List["Strategy"]
    """
    Contains vault-level information
    """

    def __init__(
        self, address: str, name: str, token: Token, strategies: List["Strategy"]
    ):
        self.address = address
        self.name = name
        self.token = token
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
    def risk_scores(self) -> VaultRisk:
        """return vault-level risk scores"""
        raise NotImplementedError()
