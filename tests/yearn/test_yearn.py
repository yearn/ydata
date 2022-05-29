import pytest
from dotenv import load_dotenv
from src.yearn import Network, Yearn

load_dotenv()

YEARN_MAINNET = Yearn(Network.Mainnet)
YEARN_FANTOM = Yearn(Network.Fantom)


@pytest.mark.parametrize("yearn", [YEARN_MAINNET, YEARN_FANTOM])
def test_load_vaults(yearn):
    assert len(yearn.vaults) > 0


@pytest.mark.parametrize("yearn", [YEARN_MAINNET, YEARN_FANTOM])
def test_load_strategies(yearn):
    assert len(yearn.strategies) > 0
