from typing import Union, List
import requests
from subgraph import SubgraphHelper
from yearn_labs.vault import Vault
from yearn_labs.strategy import Strategy
from vault_risk.scores import StrategyScore, VaultScore


class VaultRisk:
    """
    Wrapper class for the vault-level risk project
    """

    def __init__(self, subgraph: SubgraphHelper, risk_framework_url: str):
        # Yearn Subgraph
        self.subgraph = subgraph

        # Risk Framework json file
        res = requests.get(risk_framework_url)
        self.risk_framework = res.json()

    def get_strategy_scores(
        self, strategy: Union[Strategy, List[Strategy]]
    ) -> List[StrategyScore]:
        """Returns the risk metrics for each strategy"""
        pass

    def get_vault_scores(self, vault: Union[Vault, List[Vault]]) -> List[VaultScore]:
        """Returns the risk metrics for each vault"""
        pass
