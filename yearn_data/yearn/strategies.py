import time
from typing import List, Union
from decimal import Decimal
from dataclasses import dataclass
import numpy as np
import pandas as pd

from ..utils.web3 import get_contract, call, erc20_from
from ..utils.labels import get_labels
from ..utils.price import get_usdc_price
from ..yearn.vaults import Vault
from ..risk.framework import (
    RiskFrameworkScores,
    longevity_impact,
    tvl_impact,
)
from ..risk.scores import RiskScoreInterval, StrategyRisk


@dataclass
class StrategyInfo:
    riskScores: StrategyRisk
    protocols: List
    tokens: List


class Strategy:
    address: str
    name: str
    _risk_scores: RiskFrameworkScores
    vault: Union[Vault, None]

    """
    Contains strategy-level information
    """

    def __init__(self, address: str, name: str, risk_scores: RiskFrameworkScores):
        self.address = address
        self.name = name
        self._risk_scores = risk_scores
        self.vault = None

    def __repr__(self):
        return f"<Strategy name={self.name}>"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    @property
    def longevity(self) -> Decimal:
        if self.vault is None:
            vault_address = call(self.address, "vault")
        else:
            vault_address = self.vault.address
        params = call(vault_address, "strategies", self.address)
        return Decimal(time.time()) - params[1]  # activation

    @property
    def tvl(self) -> Decimal:
        if self.vault is None:
            vault_address = call(self.address, "vault")
            decimals = Decimal(call(vault_address, "decimals"))
            token_address = call(vault_address, "token")
        else:
            decimals = Decimal(self.vault.token.decimals)
            token_address = self.vault.token.address

        total_assets = Decimal(call(self.address, "estimatedTotalAssets"))
        total_assets /= 10**decimals
        usdc_price = get_usdc_price(token_address)
        return total_assets * usdc_price

    @property
    def risk_scores(self) -> StrategyRisk:
        """return strategy-level risk scores"""
        return StrategyRisk(
            TVLImpact=tvl_impact(self.tvl),
            longevityImpact=longevity_impact(self.longevity),
            **self._risk_scores.__dict__,
        )

    def risk_score(self, weights: pd.DataFrame = None) -> RiskScoreInterval:
        scores = self.risk_scores
        if weights is None:
            weights = pd.DataFrame(
                5.0 * np.ones((1, len(scores.__dict__))),
                columns=list(scores.__dict__.keys()),
            )

        samples = np.zeros(len(weights))
        for idx, record in weights.iterrows():
            samples[idx] = sum(
                v * getattr(record, k) for k, v in scores.__dict__.items()
            ) / sum(record)

        q1, q3 = np.percentile(samples, [25, 75])
        iqr = q3 - q1
        median = np.median(samples)
        return RiskScoreInterval(
            low=median - 1.5 * iqr, median=median, high=median + 1.5 * iqr
        )

    def describe(self) -> StrategyInfo:
        addresses = erc20_from(self.address)
        tokens = []
        for address in addresses:
            token = get_contract(address)
            if hasattr(token.caller, "symbol"):
                tokens.append(token.caller.symbol())
        labels = [label for address in addresses for label in get_labels(address)]
        return StrategyInfo(self.risk_scores, list(set(labels)), list(set(tokens)))
