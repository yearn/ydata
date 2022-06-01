from typing import Optional

from sqlmodel import Field, SQLModel


class Vault(SQLModel, table=True):
    id: str = Field(primary_key=True)
    address: str = Field(index=True)
    network: int
    name: str
    info: Optional[str]


class Strategy(SQLModel, table=True):
    id: str = Field(primary_key=True)
    address: str = Field(index=True)
    network: int
    name: str
    info: Optional[str]


def create_id(address: str, network: int) -> str:
    return str(int(network)) + '_' + address.lower()
