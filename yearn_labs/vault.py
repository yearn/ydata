from typing import List, NamedTuple
from .strategy import Strategy


class Token(NamedTuple):
    address: str
    decimals: int
    name: str
    symbol: str


class Vault:
    """
    Contains vault-level information
    """

    def __init__(
        self, address: str, name: str, token: Token, strategies: List[Strategy]
    ):
        self.address = address
        self.name = name
        self.token = token
        self.strategies = strategies

    def __repr__(self):
        return f"Vault({self.name})"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)
