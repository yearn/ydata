import json
import logging
import os
from decimal import Decimal
from json.decoder import JSONDecodeError
from typing import Literal, Optional, Union

from web3 import Web3
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
from web3.contract import Contract
from web3.datastructures import AttributeDict
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware

from src.constants import BLOCK_SIZE, MAX_BLOCK, USDC_DECIMALS
from src.networks import Network
from src.utils.network import client, parse_json, rate_limit, retry

logger = logging.getLogger(__name__)


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
        elif network == Network.Optimism:
            provider = os.environ["OPT_PROVIDER"]
            self.scan_url = "https://optimistic.etherscan.io/"
            self.endpoint = (
                f"https://api-optimistic.etherscan.io/api?&apiKey={os.environ['FTMSCAN_TOKEN']}"
            )
            self.oracle = "0xB082d9f4734c535D9d80536F7E87a6f4F471bF65"
        elif network == Network.Fantom:
            provider = os.environ["FTM_PROVIDER"]
            self.scan_url = "https://ftmscan.com"
            self.endpoint = (
                f"https://api.ftmscan.com/api?&apiKey={os.environ['FTMSCAN_TOKEN']}"
            )
            self.oracle = "0x57aa88a0810dfe3f9b71a9b179dd8bf5f956c46a"
        elif network == Network.Arbitrum:
            provider = os.environ["ARB_PROVIDER"]
            self.scan_url = "https://arbiscan.io"
            self.endpoint = (
                f"https://api.arbiscan.io/api?&apiKey={os.environ['ARBISCAN_TOKEN']}"
            )
            self.oracle = "0x043518ab266485dc085a1db095b8d9c2fc78e9b9"

        self.provider = Web3(Web3.HTTPProvider(provider))
        if network == Network.Optimism:
            self.provider.middleware_onion.inject(
                geth_poa_middleware, layer=0
            )

    @rate_limit()
    def fetch_abi(self, address: str) -> list[dict]:
        address = Web3.toChecksumAddress(address)
        params = {"address": address, "module": "contract", "action": "getabi"}
        response = client('get', self.endpoint, params=params)
        jsoned = parse_json(response)
        if jsoned is None:
            msg = f"Failed to fetch abi from address={address}"
            logger.error(msg)
            raise ValueError(msg)
        abi = jsoned["result"]
        try:
            return json.loads(abi)
        except JSONDecodeError as e:
            logger.error(abi)
            raise e

    @retry(
        exception=JSONDecodeError,
        exception_handler=lambda self, address: f"Failed to fetch contract for {address}",
    )
    def get_contract(self, address: str) -> Optional[Contract]:
        abi = self.fetch_abi(address)
        address = Web3.toChecksumAddress(address)
        contract = self.provider.eth.contract(address=address, abi=abi)
        return contract

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

    @rate_limit()
    def fetch_events(
        self,
        address: str,
        event_name: str,
        from_block: Union[int, Literal["latest"]] = "latest",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> list[AttributeDict]:
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

    @rate_limit()
    def erc20_tokens(
        self,
        address: str,
        from_block: Union[int, Literal["first"]] = "first",
        to_block: Union[int, Literal["latest"]] = "latest",
    ) -> list[str]:
        from_block = 0 if from_block == "first" else from_block
        to_block = MAX_BLOCK if to_block == "latest" else to_block
        params = {
            "address": address,
            "module": "account",
            "action": "tokentx",
            "startblock": str(from_block),
            "endblock": str(to_block),
        }
        response = client('get', self.endpoint, params=params)
        jsoned = parse_json(response)
        if jsoned is None:
            msg = f"Failed to fetch erc20 transfers from address={address}"
            logger.error(msg)
            return []
        txns = jsoned["result"]

        # get the tokens that were handled by the strategy
        tokens = self.__parse_erc20_transactions(txns, address)
        if tokens is None:
            return []
        return tokens

    @retry(
        exception=TypeError,
        exception_handler=lambda self, txns, address: f"Failed to fetch erc20 transfers from address={address}",
    )
    def __parse_erc20_transactions(self, txns: list[dict], address: str) -> list[str]:
        result = set({})
        try:
            for tx in txns:
                if tx["from"].lower() == address.lower():
                    token_address = tx["contractAddress"]
                    result.add(token_address.lower())
        except TypeError as e:
            logger.error(txns)
            raise e
        return list(result)

    def get_usdc_price(
        self, token_address: str, block: Union[int, Literal["latest"]] = "latest"
    ) -> Decimal:
        token_address = Web3.toChecksumAddress(token_address)
        usdc_price = self.call(
            self.oracle, "getPriceUsdcRecommended", token_address, block=block
        )
        if usdc_price is not None:
            return Decimal(usdc_price) / Decimal(10**USDC_DECIMALS)
        else:
            msg = f"Failed to fetch usdc price for token={token_address}"
            logger.error(msg)
        return Decimal(0)
