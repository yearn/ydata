from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Dict
from decimal import Decimal

from ..utils.web3 import fetch_events, ZERO_ADDRESS
from ..risk.scores import StrategyRisk, VaultRisk

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
    top_wallets: Dict


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

    @property
    def wallets(self) -> Dict[str, Decimal]:
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

        wallets = {k: max(Decimal(0), v) for k, v in wallets.items()}
        return wallets

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

        wallets = self.wallets
        wallets_tvl = sum(wallets.values())
        wallets = dict(
            sorted(wallets.items(), key=lambda item: item[1], reverse=True)[:10]
        )
        top_wallets = {k: float(v / wallets_tvl) for k, v in wallets.items()}

        return VaultInfo(self.risk_scores, protocols, tokens, top_wallets)
