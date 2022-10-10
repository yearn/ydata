from enum import Enum
from typing import Annotated, Literal, NewType, TypedDict

from typing_extensions import NotRequired

Address = NewType("Address", str)


class NetworkStr(str, Enum):
    Mainnet = "ETH"
    Fantom = "FTM"


class Data(TypedDict):
    values: Annotated[list[list[int]], 2]


class Label(TypedDict):
    __name__: str
    address: Address
    experimental: Literal["true", "false"]
    network: NetworkStr
    param: str
    vault: str
    version: str


class Field(TypedDict):
    name: str
    type: str
    typeInfo: dict
    labels: NotRequired[Label]
    config: NotRequired[dict]


class Schema(TypedDict):
    name: str
    refId: Literal["A", "B"]
    meta: dict
    fields: list[Field]


class Frame(TypedDict):
    schema: Schema
    data: Data


class Frames(TypedDict):
    frames: list[Frame]


class QueryResult(TypedDict):
    results: dict[NetworkStr, Frames]


class QueryResultMap(TypedDict):
    name: str
    network: NetworkStr
    address: Address
    values: dict[int, int]


class VaultInfo(TypedDict):
    assetType: Literal["BTC", "ETH", "Stable", "Altcoin", "Iron Bank", "Other"]


class Strategy(TypedDict):
    address: Address
    name: str
    description: str


class Token(TypedDict):
    address: Address
    name: str
    display_name: str
    symbol: str
    description: str
    decimals: int
    icon: str


class Vault(TypedDict):
    strategies: list[Strategy]
    token: Token


class Block(TypedDict):
    number: int
    timestamp: int  # seconds
