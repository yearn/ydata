from dataclasses import dataclass
from decimal import Decimal


DAYS = 60 * 60 * 24


@dataclass
class RiskFrameworkScores:
    auditScore: int = 5
    codeReviewScore: int = 5
    complexityScore: int = 5
    protocolSafetyScore: int = 5
    teamKnowledgeScore: int = 5
    testingScore: int = 5


def tvl_impact(tvl: Decimal) -> int:
    if tvl == 0:
        return 0
    elif tvl < 1_000_000:
        return 1
    elif tvl < 10_000_000:
        return 2
    elif tvl < 50_000_000:
        return 3
    elif tvl < 100_000_000:
        return 4
    else:
        return 5


def longevity_impact(longevity: Decimal) -> int:
    if longevity < 7 * DAYS:
        return 5
    elif longevity <= 30 * DAYS:
        return 4
    elif longevity < 120 * DAYS:
        return 3
    elif longevity <= 240 * DAYS:
        return 2
    else:
        return 1
