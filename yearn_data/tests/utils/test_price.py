import pytest
from ...utils.price import get_usdc_price

USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
YFI = "0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e"


@pytest.mark.parametrize("address", [USDC, YFI])
def test_get_usdc_price(address):
    assert get_usdc_price(address) > 0
