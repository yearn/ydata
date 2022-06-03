import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Union

import jsons
import pandas as pd

from src.constants import RISK_FRAMEWORK
from src.risk_framework.defi_safety import DeFiSafety
from src.risk_framework.scores import (
    StrategyRiskScores,
    VaultRiskScores,
    longevity_impact,
    tvl_impact,
)
from src.utils.network import client, parse_json
from src.yearn import Network, Strategy, Vault

logger = logging.getLogger(__name__)


@dataclass
class RiskGroup:
    id: str
    network: Network
    label: str
    codeReviewScore: float
    testingScore: float
    auditScore: float
    protocolSafetyScore: float
    complexityScore: float
    teamKnowledgeScore: float
    criteria: Dict[str, List[str]]


class RiskAnalysis:
    defi_safety: DeFiSafety
    _risk_groups: List[RiskGroup]
    _risk_weights: pd.DataFrame

    """
    Interface for providing risk-related information
    """

    def __init__(self):
        # defi safety
        self.defi_safety = DeFiSafety()

        # risk framework scores
        response = client('get', RISK_FRAMEWORK)
        jsoned = parse_json(response)
        if jsoned is None:
            msg = "Failed to load the risk framework"
            logger.debug(msg)
            raise ValueError(msg)
        self._risk_groups = [RiskGroup(**group) for group in jsoned]

        # risk weights
        self._risk_weights = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "weights.csv"), header=0
        )

    def refresh(self):
        self.defi_safety.refresh()

        response = client('get', RISK_FRAMEWORK)
        jsoned = parse_json(response)
        if jsoned is None:
            msg = "Failed to load the risk framework"
            logger.debug(msg)
            raise ValueError(msg)
        self._risk_groups = [RiskGroup(**group) for group in jsoned]

    def scores(
        self, product: Union[Strategy, Vault]
    ) -> Union[StrategyRiskScores, VaultRiskScores]:
        if isinstance(product, Strategy):
            return self.__strategy_scores(product)
        elif isinstance(product, Vault):
            return self.__vault_scores(product)
        else:
            raise TypeError("product must be either a strategy or a vault")

    def __strategy_scores(self, strategy: Strategy) -> StrategyRiskScores:
        for group in self._risk_groups:
            if group.network != strategy.network:
                continue
            name = strategy.name.lower()
            if any([exclude.lower() in name for exclude in group.criteria["exclude"]]):
                continue
            if any([include.lower() in name for include in group.criteria["nameLike"]]):
                return StrategyRiskScores(
                    auditScore=group.auditScore,
                    codeReviewScore=group.codeReviewScore,
                    complexityScore=group.complexityScore,
                    protocolSafetyScore=group.protocolSafetyScore,
                    teamKnowledgeScore=group.teamKnowledgeScore,
                    testingScore=group.testingScore,
                    TVLImpact=tvl_impact(strategy.tvl),
                    longevityImpact=longevity_impact(strategy.longevity),
                )
        return StrategyRiskScores()

    def __vault_scores(self, vault: Vault) -> VaultRiskScores:
        if len(vault.strategies) == 0:
            return VaultRiskScores()

        scores = StrategyRiskScores() * 0.0
        total_tvl = 0.0
        for strategy in vault.strategies:
            strategy_tvl = float(strategy.tvl)
            scores += self.__strategy_scores(strategy) * strategy_tvl
            total_tvl += strategy_tvl
        if total_tvl == 0:
            return VaultRiskScores()

        scores /= total_tvl

        return VaultRiskScores(
            auditScore=scores.auditScore,
            codeReviewScore=scores.codeReviewScore,
            complexityScore=scores.complexityScore,
            protocolSafetyScore=scores.protocolSafetyScore,
            teamKnowledgeScore=scores.teamKnowledgeScore,
            testingScore=scores.testingScore,
        )

    def describe(self, product: Union[Strategy, Vault]) -> str:
        # risk-related information
        if isinstance(product, Strategy):
            info = jsons.dump(product.describe())
            protocol_info = []
            for protocol in info["protocols"]:
                protocol_scores = (
                    None  # self.defi_safety.scores(protocol)  FIXME: temporary removal
                )
                protocol_info.append(
                    {
                        "name": protocol,
                        "DeFiSafetyScores": protocol_scores,
                    }
                )
            info["protocols"] = protocol_info

        elif isinstance(product, Vault):
            info = jsons.dump(product.describe())
            protocol_info = []
            for protocol in info["protocols"]:
                protocol_scores = None  # self.defi_safety.scores(protocol["name"])  FIXME: temporary removal
                protocol_info.append(
                    {
                        "name": protocol["name"],
                        "DeFiSafetyScores": protocol_scores,
                        "TVLAllocation": protocol["TVLAllocation"],
                    }
                )
            info["protocols"] = protocol_info

        else:
            raise TypeError("product must be either a strategy or a vault")

        # risk framework scores
        info["riskScores"] = self.scores(product)
        info["riskProfile"] = info["riskScores"].profile(self._risk_weights)

        # comply to json format
        info = jsons.dump(info)
        info_str = str(info).replace("'", '"').replace("None", "null")
        return info_str
