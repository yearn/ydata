import logging
from functools import cache
from typing import Literal, TypedDict

import requests

from ..networks import Network

logger = logging.getLogger(__name__)

YEARN_META_URL = 'https://meta.yearn.network'


LocalizedData = TypedDict('LocalizedData', {
    'name': str,
    'description': str
})

Localization = TypedDict('Localization', {
    'en': LocalizedData,
    'fr': LocalizedData,
    'es': LocalizedData,
    'de': LocalizedData,
    'pt': LocalizedData,
    'el': LocalizedData,
    'tr': LocalizedData,
    'vi': LocalizedData,
    'zh': LocalizedData,
    'hi': LocalizedData,
    'ja': LocalizedData,
    'id': LocalizedData,
    'ru': LocalizedData
})

StrategyMeta = TypedDict('StrategyMeta', {
    '$schema': Literal['strategy'],
    'name': str,
    'description': str,
    'addresses': list[str],
    'protocols': list[str],
    'localization': Localization
})


def fetch_strategies(network: Network = Network.Mainnet) -> list[StrategyMeta]:
    url = f'{YEARN_META_URL}/strategies/{network}/all'

    response = requests.get(url)
    if response.status_code != 200:
        logger.debug(f'Failed to fetch strategy meta from {url}')
        response.raise_for_status()
    return response.json()


@cache
def map_strategy_protocols() -> dict[str, list[str]]:
    protocols: dict[str, list[str]] = {}

    strategy_meta = fetch_strategies()
    for strategy in strategy_meta:
        for address in strategy['addresses']:
            protocols[address] = strategy['protocols']
    return protocols


def get_strategy_protocols(strategy_address: str) -> list[str]:
    protocols = map_strategy_protocols()
    return protocols.get(strategy_address, [])
