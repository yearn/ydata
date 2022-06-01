from dataclasses import dataclass
from decimal import Decimal

import numpy as np
import pandas as pd

DAYS = 60 * 60 * 24


@dataclass
class RiskProfileScores:
    low: float = 5
    median: float = 5
    high: float = 5


def tvl_impact(tvl: Decimal) -> float:
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


def longevity_impact(longevity: Decimal) -> float:
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


@dataclass
class StrategyRiskScores:
    auditScore: float = 5.0
    codeReviewScore: float = 5.0
    complexityScore: float = 5.0
    protocolSafetyScore: float = 5.0
    teamKnowledgeScore: float = 5.0
    testingScore: float = 5.0
    TVLImpact: float = 5.0
    longevityImpact: float = 5.0

    def __add__(self, other):
        new_score = StrategyRiskScores()
        for key in new_score.__dict__.keys():
            self_score = getattr(self, key)
            other_score = getattr(other, key)
            if self_score is not None and other_score is not None:
                setattr(new_score, key, self_score + other_score)
        return new_score

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __mul__(self, scalar):
        new_score = StrategyRiskScores()
        for key in new_score.__dict__.keys():
            self_score = getattr(self, key)
            if self_score is not None:
                setattr(new_score, key, self_score * scalar)
        return new_score

    def __truediv__(self, scalar):
        new_score = StrategyRiskScores()
        for key in new_score.__dict__.keys():
            self_score = getattr(self, key)
            if self_score is not None:
                setattr(new_score, key, self_score / scalar)
        return new_score

    def profile(self, weights: pd.DataFrame = None) -> RiskProfileScores:
        if weights is None:
            weights = pd.DataFrame(
                5.0 * np.ones((1, len(self.__dict__))),
                columns=list(self.__dict__.keys()),
            )
        samples = np.zeros(len(weights))
        for idx, record in weights.iterrows():
            samples[idx] = sum(
                v * getattr(record, k) for k, v in self.__dict__.items()
            ) / sum(record)

        q1, q3 = np.percentile(samples, [25, 75])
        iqr = q3 - q1
        median = np.median(samples)
        return RiskProfileScores(
            low=median - 1.5 * iqr,
            median=float(median),
            high=median + 1.5 * iqr,
        )


@dataclass
class VaultRiskScores:
    auditScore: float = 5.0
    codeReviewScore: float = 5.0
    complexityScore: float = 5.0
    protocolSafetyScore: float = 5.0
    teamKnowledgeScore: float = 5.0
    testingScore: float = 5.0

    def profile(self, weights: pd.DataFrame = None) -> RiskProfileScores:
        if weights is None:
            weights = pd.DataFrame(
                5.0 * np.ones((1, len(self.__dict__))),
                columns=list(self.__dict__.keys()),
            )
        samples = np.zeros(len(weights))
        for idx, record in weights.iterrows():
            samples[idx] = sum(
                v * getattr(record, k) for k, v in self.__dict__.items()
            ) / sum(record)

        q1, q3 = np.percentile(samples, [25, 75])
        iqr = q3 - q1
        median = np.median(samples)
        return RiskProfileScores(
            low=median - 1.5 * iqr,
            median=float(median),
            high=median + 1.5 * iqr,
        )
