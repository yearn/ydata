import os
from typing import List, Dict, Union
import json
import requests
import logging
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ['WEB3_PROVIDER']))
logger = logging.getLogger(__name__)

ABI_ENDPOINT = f"https://api.etherscan.io/api?module=contract&action=getabi&address="


def fetch_abi(address: str) -> List[Dict]:
    apiKey = os.environ["ETHERSCAN_TOKEN"]
    url = ABI_ENDPOINT + address + f"&apiKey={apiKey}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.debug(f"Failed to fetch abi from address={address}")
        response.raise_for_status()
    abi = response.json()["result"]
    return json.loads(abi)


def call(address: str, fn: str, *fn_args, block: Union[int, str] = "latest"):
    abi = fetch_abi(address)
    address = Web3.toChecksumAddress(address)
    contract = w3.eth.contract(address=address, abi=abi)
    return getattr(contract.caller, fn)(*fn_args, block_identifier=block)
