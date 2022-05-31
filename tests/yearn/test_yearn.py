import pytest
from dotenv import load_dotenv
from .tst_yearn_constants import YEARN_MAINNET, YEARN_FANTOM

load_dotenv()


@pytest.mark.parametrize("yearn", [YEARN_MAINNET, YEARN_FANTOM])
def test_load_vaults(yearn):
    assert len(yearn.vaults) > 0


@pytest.mark.parametrize("yearn", [YEARN_MAINNET, YEARN_FANTOM])
def test_load_strategies(yearn):
    assert len(yearn.strategies) > 0
