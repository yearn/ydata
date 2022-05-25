import os
from typing import Set, List, Dict, Union
from web3 import Web3
import jsons
import pandas as pd
import requests
import logging
from dotenv import load_dotenv

from .vaults import Vault, Token
from .strategies import Strategy
from ..risk.framework import RiskFrameworkScores
from ..risk.defi_safety import DeFiSafety

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
    _risk_weights: pd.DataFrame
    _defi_safety: DeFiSafety

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

        # fetch risk metric weights
        # TODO: decide where to put the csv
        # maybe we should create a RiskAnalysis class to separate out all the risk-related stuff?
        sample_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'sample_risk_weights.csv'
        )
        self._risk_weights = pd.read_csv(sample_path, header=0)

        # fetch defi safety scores
        self._defi_safety = DeFiSafety()

    def get_framework_scores(self, strategy_name: str) -> RiskFrameworkScores:
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
                    risk_scores=self.get_framework_scores(strategy['name']),
                )
                for strategy in vault['strategies']
            ]
            self._vaults.add(
                Vault(
                    address=vault['address'],
                    name=vault['name'],
                    token=token,
                    inception=vault['inception'],
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

    def describe(self, product: Union[Strategy, Vault]) -> str:
        if isinstance(product, Strategy):
            return self.__describe_strategy(product)
        elif isinstance(product, Vault):
            return self.__describe_vault(product)
        else:
            raise NotImplementedError("Product should be a strategy or a vault")

    def __describe_strategy(self, strategy: Strategy) -> str:
        info = strategy.describe()

        # append defi safety scores
        protocol_info = []
        for protocol in info.protocols:
            # arithmetic average of candidate scores
            candidates = self._defi_safety.scores(protocol)
            if len(candidates) > 0:
                scores = sum(candidates.values()) / len(candidates)
            else:
                continue
            protocol_info.append({"name": protocol, "DeFiSafetyScores": scores})
        info.protocols = protocol_info

        # append risk score interval
        info_json = jsons.dump(info)
        info_json['overallScore'] = jsons.dump(strategy.risk_score(self._risk_weights))
        return str(info_json).replace("\'", "\"").replace("None", "null")

    def __describe_vault(self, vault: Vault) -> str:
        info = vault.describe()

        # append defi safety scores
        no_defi_safety = []
        for protocol in info.protocols:
            # arithmetic average of candidate scores
            candidates = self._defi_safety.scores(protocol["name"])
            if len(candidates) > 0:
                scores = sum(candidates.values()) / len(candidates)
            else:
                no_defi_safety.append(protocol)
                continue
            protocol["DeFiSafetyScores"] = scores
        for protocol in no_defi_safety:
            info.protocols.remove(protocol)

        # append risk score interval
        info_json = jsons.dump(info)
        info_json['overallScore'] = jsons.dump(vault.risk_score(self._risk_weights))
        return str(info_json).replace("\'", "\"").replace("None", "null")
