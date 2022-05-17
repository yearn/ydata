from dataclasses import dataclass

from .framework import RiskFrameworkScores


@dataclass
class StrategyRisk(RiskFrameworkScores):
    TVLImpact: float = 5
    longevityImpact: float = 5

    def __add__(self, other):
        new_score = StrategyRisk()
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
        new_score = StrategyRisk()
        for key in new_score.__dict__.keys():
            self_score = getattr(self, key)
            if self_score is not None:
                setattr(new_score, key, self_score * scalar)
        return new_score

    def __truediv__(self, scalar):
        new_score = StrategyRisk()
        for key in new_score.__dict__.keys():
            self_score = getattr(self, key)
            if self_score is not None:
                setattr(new_score, key, self_score / scalar)
        return new_score


@dataclass
class VaultRisk(RiskFrameworkScores):
    pass
