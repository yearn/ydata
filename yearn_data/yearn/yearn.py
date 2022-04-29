import os
from typing import Set, List
from web3 import Web3
import requests
import logging
from dotenv import load_dotenv

from .vaults import Vault, Token
from .strategies import Strategy
from .accounts import Account

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ['WEB3_PROVIDER']))
logger = logging.getLogger(__name__)

API_ENDPOINT = "https://api.yearn.finance/v1/chains/"


class Yearn:
    endpoint: str
    _accounts: Set[Account]
    _vaults: Set[Vault]
    _strategies: Set[Strategy]

    """
    Interface for providing information about our assets and clients
    """

    def __init__(self):
        self.endpoint = API_ENDPOINT + f"{w3.eth.chain_id}/"
        self._accounts = None
        self._vaults = None
        self._strategies = None

    def load_vaults(self):
        url = self.endpoint + "vaults/all"
        response = requests.get(url)
        if response.status_code != 200:
            logger.debug("Failed to load vaults from api")
            raise response.raise_for_status()
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
