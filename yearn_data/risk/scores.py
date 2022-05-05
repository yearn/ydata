from dataclasses import dataclass

from .framework import RiskFrameworkScores


@dataclass
class StrategyRisk(RiskFrameworkScores):
    TVLImpact: int = 5
    longevityImpact: int = 5


@dataclass
class VaultRisk(RiskFrameworkScores):
    pass
