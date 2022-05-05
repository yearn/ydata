import os
from typing import Set, List, Dict
from web3 import Web3
import requests
import logging
from dotenv import load_dotenv

from .vaults import Vault, Token
from .strategies import Strategy
from ..risk.framework import RiskFrameworkScores

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ['WEB3_PROVIDER']))
logger = logging.getLogger(__name__)

API_ENDPOINT = "https://api.yearn.finance/v1/chains/"
RISK_FRAMEWORK = (
    "https://raw.githubusercontent.com/yearn/yearn-watch/main/utils/risks.json"
)


class Yearn:
    endpoint: str
    _vaults: Set[Vault]
    _strategies: Set[Strategy]
    _risk_framework: List[Dict]

    """
    Interface for providing information about our assets and clients
    """

    def __init__(self):
        self.endpoint = API_ENDPOINT + f"{w3.eth.chain_id}/"
        self._vaults = None
        self._strategies = None

        # fetch risk framework scores
        response = requests.get(RISK_FRAMEWORK)
        if response.status_code != 200:
            logger.debug("Failed to load the risk framework")
            response.raise_for_status()
        self._risk_framework = [
            score for score in response.json() if score['network'] == w3.eth.chain_id
        ]

    def get_strategy_scores(self, strategy_name: str) -> RiskFrameworkScores:
        name = strategy_name.lower()
        for group in self._risk_framework:
            if any(
                [exclude.lower() in name for exclude in group['criteria']['exclude']]
            ):
                continue
            if any(
                [include.lower() in name for include in group['criteria']['nameLike']]
            ):
                return RiskFrameworkScores(
                    auditScore=group['auditScore'],
                    codeReviewScore=group['codeReviewScore'],
                    complexityScore=group['complexityScore'],
                    protocolSafetyScore=group['protocolSafetyScore'],
                    teamKnowledgeScore=group['teamKnowledgeScore'],
                    testingScore=group['testingScore'],
                )
        return RiskFrameworkScores()

    def load_vaults(self):
        url = self.endpoint + "vaults/all"
        response = requests.get(url)
        if response.status_code != 200:
            logger.debug("Failed to load vaults from api")
            response.raise_for_status()
        data = response.json()

        self._vaults = set({})
        self._strategies = set({})
        for vault in data:
            if vault['type'] != 'v2':  # get only the V2 vaults
                continue

            _token = vault['token']
            token = Token(
                address=_token['address'],
                decimals=_token['decimals'],
                name=_token['name'],
                symbol=_token['display_name'],
            )
            strategies = [
                Strategy(
                    address=strategy['address'],
                    name=strategy['name'],
                    risk_scores=self.get_strategy_scores(strategy['name']),
                )
                for strategy in vault['strategies']
            ]
            self._vaults.add(
                Vault(
                    address=vault['address'],
                    name=vault['name'],
                    token=token,
                    strategies=strategies,
                )
            )
            self._strategies.update(strategies)

    @property
    def vaults(self) -> List[Vault]:
        if self._vaults is None:
            self.load_vaults()
        return list(self._vaults)

    @property
    def strategies(self) -> List[Strategy]:
        if self._strategies is None:
            self.load_vaults()
        return list(self._strategies)
