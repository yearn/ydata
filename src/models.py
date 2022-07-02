from typing import Optional

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


def create_id(id: str, network: int) -> str:
    return str(int(network)) + '_' + id.lower()


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

    allocations: list["StrategyAllocation"] = Relationship(
        back_populates="strategy",
    )


class RiskGroup(SQLModel, table=True):
    id: str = Field(primary_key=True)
    network: int
    label: str
    auditScore: float
    codeReviewScore: float
    testingScore: float
    protocolSafetyScore: float
    complexityScore: float
    teamKnowledgeScore: float
    criteria: dict = Field(default={}, sa_column=Column(JSON))

    allocations: list["StrategyAllocation"] = Relationship(
        back_populates="riskGroup",
    )


class StrategyAllocation(SQLModel, table=True):
    id: str = Field(primary_key=True)
    method: str
    currentTVL: float
    availableTVL: float

    strategy_id: str = Field(default=None, foreign_key="strategy.id")
    strategy: Strategy = Relationship(back_populates="allocations")

    riskGroup_id: str = Field(default=None, foreign_key="riskgroup.id")
    riskGroup: RiskGroup = Relationship(back_populates="allocations")
