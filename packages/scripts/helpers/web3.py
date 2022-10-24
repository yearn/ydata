import json
import logging
import os
from json.decoder import JSONDecodeError
from typing import Literal, Optional, Union

import pandas as pd
from helpers.constants import Network
from helpers.network import client, parse_json, rate_limit, retry
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware

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
            self.endpoint = f"https://api-optimistic.etherscan.io/api?&apiKey={os.environ['FTMSCAN_TOKEN']}"
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
            self.provider.middleware_onion.inject(geth_poa_middleware, layer=0)

    @rate_limit()
    def fetch_abi(self, address: str) -> list[dict]:
        address = Web3.toChecksumAddress(address)
        params = {"address": address, "module": "contract", "action": "getabi"}
        response = client("get", self.endpoint, params=params)
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
            if abi == "Contract source code not verified":
                raise ValueError(abi)
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

    def get_closest_block(
        self, target: Union[int, pd.Timestamp], threshold: int = 600
    ) -> int:
        if isinstance(target, pd.Timestamp):
            target = int(target.value) // 1e9
        block_ts = 0
        low = 0
        high = self.provider.eth.getBlock("latest").number
        while abs(target - block_ts) > threshold:
            mid = (low + high) // 2
            block = self.provider.eth.getBlock(mid)
            block_ts = block.timestamp
            if block_ts >= target:
                high = mid
            else:
                low = mid
            if block.number == 0:
                raise ValueError(
                    "target timestamp seems to be earlier than the genesis block"
                )
        return block.number
