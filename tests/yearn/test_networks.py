import pytest
from dotenv import load_dotenv

from src.yearn import Web3Provider

from .tst_yearn_constants import (
    CRV3_VAULT,
    USDC_ARBITRUM,
    USDC_FANTOM,
    USDC_MAINNET,
    USDC_VAULT,
    WFTM_VAULT,
)

load_dotenv()


@pytest.mark.parametrize("network, address", [USDC_VAULT, WFTM_VAULT, CRV3_VAULT])
def test_fetch_abi(network, address):
    w3 = Web3Provider(network)
    abi = w3.fetch_abi(address)
    assert any([f["name"] == "Transfer" for f in abi])


@pytest.mark.parametrize("network, address", [USDC_VAULT, WFTM_VAULT, CRV3_VAULT])
def test_call(network, address):
    w3 = Web3Provider(network)
    value = w3.call(address, "performanceFee")
    assert value == 2000


@pytest.mark.parametrize("num_blocks", [100000])
@pytest.mark.parametrize("network, address", [USDC_VAULT, WFTM_VAULT, CRV3_VAULT])
def test_fetch_events(network, address, num_blocks):
    w3 = Web3Provider(network)
    current_block = w3.provider.eth.get_block_number()
    from_block = current_block - num_blocks
    events = w3.fetch_events(address, "Transfer", from_block)
    assert len(events) > 0


@pytest.mark.parametrize("num_blocks", [100000])
@pytest.mark.parametrize("network, address", [USDC_VAULT, WFTM_VAULT, CRV3_VAULT])
def test_erc20_tokens(network, address, num_blocks):
    w3 = Web3Provider(network)
    current_block = w3.provider.eth.get_block_number()
    from_block = current_block - num_blocks
    addresses = w3.erc20_tokens(address, from_block)
    assert len(addresses) > 0


@pytest.mark.parametrize("network, address", [USDC_MAINNET, USDC_FANTOM, USDC_ARBITRUM])
def test_get_usdc_price(network, address):
    w3 = Web3Provider(network)
    assert w3.get_usdc_price(address) > 0
