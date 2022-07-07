import logging
from dataclasses import dataclass
from decimal import Decimal

import numpy as np

from src.risk_framework.analysis import RiskAnalysis, RiskGroup
from src.utils.web3 import Web3Provider
from src.yearn.strategies import Strategy
from src.yearn.yearn import Yearn

logger = logging.getLogger(__name__)


def median_to_tvl(group: RiskGroup) -> Decimal:
    _scores = [
        group.auditScore,
        group.codeReviewScore,
        group.complexityScore,
        group.protocolSafetyScore,
        group.teamKnowledgeScore,
        group.testingScore,
    ]
    median = np.median(_scores)
    if median > 4:
        return Decimal(0)
    elif median > 3:
        return Decimal(1_000_000)
    elif median > 2:
        return Decimal(10_000_000)
    elif median > 1:
        return Decimal(50_000_000)
    else:
        return Decimal(100_000_000)


@dataclass
class StrategyAllocation:
    strategy: Strategy
    riskGroup: RiskGroup
    currentTVL: Decimal  # value in WANT
    availableTVL: Decimal
    currentUSDC: Decimal  # value in USDC
    availableUSDC: Decimal


class RiskManager:
    yearn: Yearn
    analysis: RiskAnalysis

    """
    Interface for providing portfolio recommendations
    """

    def __init__(self, yearn: Yearn):
        # Yearn instance
        self.yearn = yearn

        # Risk Analysis
        self.analysis = RiskAnalysis()

    def refresh(self):
        self.yearn.refresh()
        self.analysis.refresh()

    def median_score_allocation(self) -> list[StrategyAllocation]:
        # aggregate TVL by risk group
        group_tvl = {
            group.id: Decimal(0.0)
            for group in self.analysis.risk_groups
            if group.network == self.yearn.network
        }
        for strategy in self.yearn.strategies:
            name = strategy.name.lower()
            for group in self.analysis.risk_groups:
                if group.network != strategy.network:
                    continue
                if any(
                    [exclude.lower() in name for exclude in group.criteria["exclude"]]
                ):
                    continue
                if any(
                    [include.lower() in name for include in group.criteria["nameLike"]]
                ):
                    group_tvl[group.id] += strategy.tvl

        # iterate over strategies
        allocations: dict[str, StrategyAllocation] = {}
        for strategy in self.yearn.strategies:
            name = strategy.name.lower()
            for group in self.analysis.risk_groups:
                if group.network != strategy.network:
                    continue
                if any(
                    [exclude.lower() in name for exclude in group.criteria["exclude"]]
                ):
                    continue
                if any(
                    [include.lower() in name for include in group.criteria["nameLike"]]
                ):
                    max_tvl = median_to_tvl(group)
                    available_tvl = max(Decimal(0.0), max_tvl - group_tvl[group.id])
                    strategy_tvl = strategy.tvl

                    # get usdc price of underlying
                    w3 = Web3Provider(self.yearn.network)
                    if strategy.vault is None:
                        vault_address = w3.call(strategy.address, "vault")
                        if vault_address is None:
                            msg = f"Failed to load vault address from strategy {strategy.name}"
                            logger.debug(msg)
                            continue
                        token_address = w3.call(vault_address, "token")
                    else:
                        token_address = strategy.vault.token.address
                    usdc_price = w3.get_usdc_price(token_address)

                    if strategy.address in allocations:
                        allocation = allocations[strategy.address]
                        if available_tvl < allocation.availableTVL:
                            allocations[strategy.address] = StrategyAllocation(
                                strategy=strategy,
                                riskGroup=group,
                                currentTVL=strategy_tvl / usdc_price,
                                availableTVL=available_tvl / usdc_price,
                                currentUSDC=strategy_tvl,
                                availableUSDC=available_tvl,
                            )
                    else:
                        allocations[strategy.address] = StrategyAllocation(
                            strategy=strategy,
                            riskGroup=group,
                            currentTVL=strategy_tvl / usdc_price,
                            availableTVL=available_tvl / usdc_price,
                            currentUSDC=strategy.tvl,
                            availableUSDC=available_tvl,
                        )
        return list(allocations.values())
