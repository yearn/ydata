from dataclasses import dataclass
from typing import Dict, List, Union
import requests
import logging

from .defi_safety_protocol import defi_safety_protocol

logger = logging.getLogger(__name__)

API_ENDPOINT = (
    'https://www.defisafety.com/api/pqrs?status=Active&reviewStatus=Completed'
)

protocol_to_defi_safety_protocol_map = {
    '1inch': defi_safety_protocol['1inch.exchange'],
    '1inch.exchange': defi_safety_protocol['1inch.exchange'],
    '88mph': defi_safety_protocol['88mph v3.0'],
    'aave': defi_safety_protocol['aave v3'],
    'aave v2': defi_safety_protocol['aave v2'],
    'alphahomora': defi_safety_protocol['alpha homora v2'],
    'angleprotocol': None,
    'balancer': defi_safety_protocol['balancer v2'],
    'compound': defi_safety_protocol['compound'],
    'compoundfinance': defi_safety_protocol['compound'],
    'convexfinance': defi_safety_protocol['convex finance'],
    'creamfinance': defi_safety_protocol['c.r.e.a.m finance v2'],
    'curve.fi': defi_safety_protocol['curve finance'],
    'curvefinance': defi_safety_protocol['curve finance'],
    'dydx': defi_safety_protocol['dydx layer 2'],
    'fei protocol': None,
    'fiat dao': None,
    'hegic': defi_safety_protocol['hegic v8888'],
    'idle.finance': defi_safety_protocol['idle v4'],
    'idlefinance': defi_safety_protocol['idle v4'],
    'inverse finance': defi_safety_protocol['inverse finance'],
    'inversefinance': defi_safety_protocol['inverse finance'],
    'iron bank': None,
    'ironbank': None,
    'keeperdao': None,
    'league dao': None,
    'lido': defi_safety_protocol['lido'],
    'lidofinance': defi_safety_protocol['lido'],
    'liquity': defi_safety_protocol['liquity'],
    'maker': defi_safety_protocol['makerdao'],
    'makerdao': defi_safety_protocol['makerdao'],
    'mushroomfinance': None,
    'notional finance': defi_safety_protocol['notional finance'],
    'old contract': None,
    'origin protocol': defi_safety_protocol['origin'],
    'pooltogether': defi_safety_protocol['pooltogether v4'],
    'reflexer finance': defi_safety_protocol['reflexer finance'],
    'reserve protocol': None,
    'shapeshift': defi_safety_protocol['shapeshift'],
    'sushi': defi_safety_protocol['sushiswap  v2'],
    'sushiswap': defi_safety_protocol['sushiswap  v2'],
    'synthetix': defi_safety_protocol['synthetix pq'],
    'tokemak': defi_safety_protocol['tokemak'],
    'trusttoken': None,
    'uniswap': defi_safety_protocol['uniswap v3'],
    'universe': None,
    'usdc': None,
    'vaults': None,
    'vesper finance': defi_safety_protocol['vesper'],
    'vesperfinance': defi_safety_protocol['vesper'],
    'wrapped bitcoin': None,
    'yearn.finance': defi_safety_protocol['yearn finance v2'],
    'ygov.finance': None,
}


@dataclass
class DeFiSafetyScores:
    overallScore: float
    contractsAndTeamScore: Union[float, None] = None
    documentationScore: Union[float, None] = None
    testingScore: Union[float, None] = None
    securityScore: Union[float, None] = None
    adminControlsScore: Union[float, None] = None
    oraclesScore: Union[float, None] = None

    def __add__(self, other):
        new_score = DeFiSafetyScores(self.overallScore + other.overallScore)
        for key in new_score.__dict__.keys():
            if key == 'overallScore':
                continue
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

    def __truediv__(self, scalar):
        new_score = DeFiSafetyScores(self.overallScore / scalar)
        for key in new_score.__dict__.keys():
            if key == 'overallScore':
                continue
            self_score = getattr(self, key)
            if self_score is not None:
                setattr(new_score, key, self_score / scalar)
        return new_score


class DeFiSafety:
    _scores: Dict[str, DeFiSafetyScores]

    """
    Protocol risk scores from DeFi Safety
    """

    def __init__(self):
        self._scores = None

    def load_scores(self):
        pqrs = []
        offset = 0
        no_data = False
        while not no_data:
            url = API_ENDPOINT + '&offset=' + str(offset)
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()['data']
                no_data = len(data) == 0
                pqrs.extend(data)
                offset += 20
            else:
                break
        self._scores = {}
        for pqr in pqrs:
            scores = DeFiSafetyScores(pqr['overallScore'])
            for score in pqr['breakdowns']:
                name = score['name'].lower()
                score = score['percentage']
                if score is not None:
                    score = float(score)

                if 'team' in name:
                    scores.contractsAndTeamScore = score
                elif 'documentation' in name:
                    scores.documentationScore = score
                elif 'test' in name:
                    scores.testingScore = score
                elif 'security' in name:
                    scores.securityScore = score
                elif 'control' in name:
                    scores.adminControlsScore = score
                elif 'oracle' in name:
                    scores.oraclesScore = score
            self._scores[pqr['title']] = scores

    @property
    def protocols(self) -> List[str]:
        if self._scores is None:
            self.load_scores()
        return list(self._scores.keys())

    def scores(self, name: str) -> Dict[str, DeFiSafetyScores]:
        if self._scores is None:
            self.load_scores()
        candidates = {}
        for k, v in self._scores.items():
            name_lower = name.lower()
            mapper = protocol_to_defi_safety_protocol_map
            is_matching_protocol = mapper.get(name_lower) == k

            if is_matching_protocol or name_lower in k.lower():
                candidates[k] = v
                break
        return candidates
