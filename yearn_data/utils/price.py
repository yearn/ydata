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

WETH = {
    Network.Mainnet: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    Network.Fantom: '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83',
    Network.Arbitrum: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
}
USDC = {
    Network.Mainnet: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    Network.Fantom: '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
    Network.Arbitrum: '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
}
USDC_DECIMALS = 6
UNISWAPV2_ROUTER = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'


def get_usdc_price(token_address: str, block: Union[int, str] = "latest") -> Decimal:
    weth = WETH[Network(w3.eth.chain_id)]
    usdc = USDC[Network(w3.eth.chain_id)]
    if token_address == weth:
        path = [weth, usdc]
    else:
        path = [token_address, weth, usdc]
    fees = Decimal(0.997) ** (len(path) - 1)

    decimals = call(token_address, "decimals")
    amount = 10**decimals
    quotes = call(UNISWAPV2_ROUTER, "getAmountsOut", amount, path, block=block)
    price = Decimal(quotes[-1]) / 10**USDC_DECIMALS
    return price / fees
