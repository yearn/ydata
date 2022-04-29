import os
import pytest
from web3 import Web3
from ...utils.web3 import fetch_abi, call
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ['WEB3_PROVIDER']))

USDC_VAULT = "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
DAI_VAULT = "0xdA816459F1AB5631232FE5e97a05BBBb94970c95"


@pytest.mark.parametrize("address", [USDC_VAULT, DAI_VAULT])
def test_fetch_abi(address):
    abi = fetch_abi(address)
    assert any([f["name"] == "Transfer" for f in abi])


@pytest.mark.parametrize("address", [USDC_VAULT, DAI_VAULT])
def test_fetch_value(address):
    value = call(address, "performanceFee")
    assert value == 2000
