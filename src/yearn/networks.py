import json
import logging
import os
from decimal import Decimal
from enum import IntEnum
from json import JSONDecodeError
from typing import Dict, List, Literal, Union

import requests
from requests.exceptions import HTTPError
from web3 import Web3
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
from web3.contract import Contract
from web3.datastructures import AttributeDict
from web3.exceptions import ContractLogicError

from src.constants import BLOCK_SIZE, HEADERS, MAX_BLOCK, USDC_DECIMALS

logger = logging.getLogger(__name__)


class Network(IntEnum):
    Mainnet = 1
    Fantom = 250


class Web3Provider:
    chain_id: Network
    endpoint: str
    provider: Web3

    """
    Interface for interacting with on-chain data
    """

    def __init__(self, network: Network):
        self.chain_id = network
        if network == Network.Mainnet:
            provider = os.environ["ETH_PROVIDER"]
            self.scan_url = "https://etherscan.io"
            self.endpoint = (
                f"https://api.etherscan.io/api?&apiKey={os.environ['ETHERSCAN_TOKEN']}"
            )
            self.oracle = "0x83d95e0d5f402511db06817aff3f9ea88224b030"
        elif network == Network.Fantom:
            provider = os.environ["FTM_PROVIDER"]
            self.scan_url = "https://ftmscan.com"
            self.endpoint = (
                f"https://api.ftmscan.com/api?&apiKey={os.environ['FTMSCAN_TOKEN']}"
            )
            self.oracle = "0x57aa88a0810dfe3f9b71a9b179dd8bf5f956c46a"
        self.provider = Web3(Web3.HTTPProvider(provider))

    def fetch_abi(self, address: str) -> List[Dict]:
        address = Web3.toChecksumAddress(address)
        params = {"address": address, "module": "contract", "action": "getabi"}
        response = requests.get(self.endpoint, params)
        if response.status_code != 200:
            logger.debug(f"Failed to fetch abi from address={address}")
            response.raise_for_status()
        abi = response.json()["result"]
        return json.loads(abi)

    def get_contract(self, address: str) -> Union[Contract, None]:
        try:
            abi = self.fetch_abi(address)
            address = Web3.toChecksumAddress(address)
            return self.provider.eth.contract(address=address, abi=abi)
        except (JSONDecodeError, HTTPError):
            logger.error(f"Failed to fetch contract for {address}")
        return None

    def call(
        self,
        address: str,
        fn: str,
        *fn_args,
        block: Union[int, Literal["latest"]] = "latest",
    ):
        contract = self.get_contract(address)
        if contract is None:
            return None
        try:
            return getattr(contract.caller, fn)(*fn_args, block_identifier=block)
        except ContractLogicError:
            return None

    def fetch_events(
        self,
        address: str,
        event_name: str,
        from_block: Union[int, Literal["latest"]] = "latest",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> List[AttributeDict]:
        # get event abi
        contract = self.get_contract(address)
        if contract is None:
            return []
        event = getattr(contract.events, event_name)
        event_abi = event._get_event_abi()
        event_abi_codec = event.web3.codec

        if from_block == "latest":
            from_block = self.provider.eth.get_block("latest")["number"]
        if to_block == "latest":
            to_block = self.provider.eth.get_block("latest")["number"]

        events = []
        for _from_block in range(from_block, to_block, BLOCK_SIZE):
            _to_block = min(to_block, _from_block + BLOCK_SIZE)

            _, event_filter_params = construct_event_filter_params(
                event_abi,
                event_abi_codec,
                contract_address=event.address,
                fromBlock=_from_block,
                toBlock=_to_block,
            )

            # call node over JSON-RPC API
            logs = event.web3.eth.get_logs(event_filter_params)

            # convert raw binary event data to easily manipulable Python objects
            events.extend(
                [get_event_data(event_abi_codec, event_abi, entry) for entry in logs]
            )

        return events

    def erc20_tokens(
        self,
        address: str,
        from_block: Union[int, Literal["first"]] = "first",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> List[str]:
        from_block = 0 if from_block == "first" else from_block
        to_block = MAX_BLOCK if to_block == "latest" else to_block
        params = {
            "address": address,
            "module": "account",
            "action": "tokentx",
            "startblock": str(from_block),
            "endblock": str(to_block),
        }
        response = requests.get(self.endpoint, params)
        if response.status_code != 200:
            logger.debug(f"Failed to fetch erc20 transfers from address={address}")
            response.raise_for_status()
        txns = response.json()["result"]

        # get the tokens that were handled by the strategy
        result = set({})
        for tx in txns:
            if tx["from"].lower() == address.lower():
                token_address = tx["contractAddress"]
                result.add(token_address.lower())
        return list(result)

    def get_usdc_price(
        self, token_address: str, block: Union[int, Literal["latest"]] = "latest"
    ) -> Decimal:
        token_address = Web3.toChecksumAddress(token_address)
        usdc_price = Decimal(
            self.call(
                self.oracle, "getPriceUsdcRecommended", token_address, block=block
            )
        )
        return usdc_price / Decimal(10**USDC_DECIMALS)

    def get_scan_labels(self, address: str) -> List[str]:
        url = self.scan_url + f"/address/{address}"
        try:
            response = requests.get(url, headers=HEADERS)
        except HTTPError:
            logger.debug(f"Failed to get labels from address={address}")
            return []
        if response.status_code != 200:
            logger.debug(f"Failed to get labels from address={address}")
            return []
        text = response.text

        labels = []
        while True:
            try:
                text = text[text.index("/accounts/label/") :]
                text = text[text.index(">") + 1 :]
                label = text[: text.index("<")].strip()
                labels.append(label)
            except:
                break
        return labels
