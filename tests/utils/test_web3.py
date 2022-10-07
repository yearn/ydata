import os

import pytest
from dotenv import load_dotenv

from src.utils.web3 import Web3Provider

from ..constants import (CRV3_VAULT_ADDRESS, USDC_VAULT_ADDRESS,
                         WFTM_VAULT_ADDRESS)

BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

addresses = [USDC_VAULT_ADDRESS, WFTM_VAULT_ADDRESS, CRV3_VAULT_ADDRESS]


@pytest.mark.parametrize("network, address", addresses)
def test_fetch_abi(network, address):
    w3 = Web3Provider(network)
    abi = w3.fetch_abi(address)
    assert any([f["name"] == "Transfer" for f in abi])


@pytest.mark.parametrize("network, address", addresses)
def test_call(network, address):
    w3 = Web3Provider(network)
    value = w3.call(address, "performanceFee")
    assert value == 2000
