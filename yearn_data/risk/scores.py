from dataclasses import dataclass

from .framework import RiskFrameworkScores


@dataclass
class StrategyRisk(RiskFrameworkScores):
    TVLImpact: float = 5
    longevityImpact: float = 5


@dataclass
class VaultRisk(RiskFrameworkScores):
    pass
