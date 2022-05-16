import os
from typing import Union
from decimal import Decimal
from web3 import Web3
import logging
from dotenv import load_dotenv

from ..networks import Network
from ..utils.web3 import call

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ['WEB3_PROVIDER']))
logger = logging.getLogger(__name__)

ORACLE = {
    Network.Mainnet: '0x83d95e0d5f402511db06817aff3f9ea88224b030',
    Network.Fantom: '0x57aa88a0810dfe3f9b71a9b179dd8bf5f956c46a',
}
USDC_DECIMALS = 6


def get_usdc_price(token_address: str, block: Union[int, str] = "latest") -> Decimal:
    token_address = Web3.toChecksumAddress(token_address)
    oracle = ORACLE[Network(w3.eth.chain_id)]
    usdc_price = Decimal(
        call(oracle, "getPriceUsdcRecommended", token_address, block=block)
    )
    return usdc_price / Decimal(10**USDC_DECIMALS)
