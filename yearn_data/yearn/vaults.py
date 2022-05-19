from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Dict, Tuple
from decimal import Decimal
import numpy as np
import pandas as pd

from ..utils.web3 import fetch_events, ZERO_ADDRESS
from ..risk.scores import RiskScoreInterval, StrategyRisk, VaultRisk

if TYPE_CHECKING:
    from .strategies import Strategy


@dataclass
class Token:
    address: str
    decimals: int
    name: str
    symbol: str


@dataclass
class VaultInfo:
    riskScores: VaultRisk
    protocols: List
    tokens: List
    topWallets: List


class Vault:
    address: str
    name: str
    token: Token
    inception: int
    strategies: List["Strategy"]
    """
    Contains vault-level information
    """

    def __init__(
        self,
        address: str,
        name: str,
        token: Token,
        inception: int,
        strategies: List["Strategy"],
    ):
        self.address = address
        self.name = name
        self.token = token
        self.inception = int(inception)
        self.strategies = strategies

        # set vault to self for its strategies
        for strategy in self.strategies:
            strategy.vault = self

    def __repr__(self):
        return f"<Vault name={self.name}>"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    @property
    def risk_scores(self) -> VaultRisk:
        """return vault-level risk scores"""
        if len(self.strategies) == 0:
            return VaultRisk()

        strategy_scores = [strat.risk_scores for strat in self.strategies]
        strategy_tvl = [float(strat.tvl) for strat in self.strategies]
        vault_tvl = sum(strategy_tvl)
        if vault_tvl == 0:
            return VaultRisk()

        # TVL-weighted
        vault_scores = StrategyRisk() * 0.0  # reset scores to zero
        for scores, tvl in zip(strategy_scores, strategy_tvl):
            vault_scores += scores * tvl
        vault_scores /= vault_tvl
        return VaultRisk(
            vault_scores.auditScore,
            vault_scores.codeReviewScore,
            vault_scores.complexityScore,
            vault_scores.protocolSafetyScore,
            vault_scores.teamKnowledgeScore,
            vault_scores.testingScore,
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

    @property
    def wallets(self) -> List[Tuple[str, Decimal]]:
        # FIXME: currently assumes that the share price does not change
        events = fetch_events(self.address, "Transfer", self.inception)
        denom = 10**self.token.decimals

        wallets: Dict[str, Decimal] = {}
        for event in events:
            if event['args']['sender'] == ZERO_ADDRESS:  # deposits
                deposit = event['args']
                address = deposit['receiver']
                shares = Decimal(deposit['value'] / denom)
                if address in wallets:
                    wallets[address] += shares
                else:
                    wallets[address] = shares
            elif event['args']['receiver'] == ZERO_ADDRESS:  # withdrawals
                withdrawal = event['args']
                address = withdrawal['sender']
                shares = Decimal(withdrawal['value'] / denom)
                if address in wallets:
                    wallets[address] -= shares
                else:
                    wallets[address] = -shares

        return [(k, max(Decimal(0), v)) for k, v in wallets.items()]

    def describe(self) -> VaultInfo:
        _protocols: Dict[str, float] = {}
        _tokens: Dict[str, float] = {}
        total_tvl = 0.0
        # TVL distribution of protocols and tokens
        for strategy in self.strategies:
            info = strategy.describe()
            tvl = float(strategy.tvl)
            total_tvl += tvl
            for ptl in info.protocols:
                if ptl in _protocols:
                    _protocols[ptl] += tvl
                else:
                    _protocols[ptl] = tvl
            for tkn in info.tokens:
                if tkn in _tokens:
                    _tokens[tkn] += tvl
                else:
                    _tokens[tkn] = tvl
        if total_tvl > 0:
            _protocols = {k: v / total_tvl for k, v in _protocols.items()}
            _tokens = {k: v / total_tvl for k, v in _tokens.items()}
        protocols = [{"Name": k, "TVL Ratio": v} for k, v in _protocols.items()]
        tokens = [{"Name": k, "TVL Ratio": v} for k, v in _tokens.items()]

        # wallet TVL distribution
        wallets = self.wallets
        wallets_tvl = sum([wallet[1] for wallet in wallets])
        wallets = list(sorted(wallets, key=lambda item: item[1], reverse=True)[:10])
        top_wallets = [
            (wallet[0], float(wallet[1] / wallets_tvl)) for wallet in wallets
        ]

        return VaultInfo(self.risk_scores, protocols, tokens, top_wallets)
