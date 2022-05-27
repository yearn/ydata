from typing import Optional
from sqlmodel import Field, SQLModel


class Vault(SQLModel, table=True):
    address: str = Field(primary_key=True)
    network: int
    name: str
    info: Optional[str]


class Strategy(SQLModel, table=True):
    address: str = Field(primary_key=True)
    network: int
    name: str
    info: Optional[str]
