import pytest
from dotenv import load_dotenv

from ..constants import DAYS, STRAT1, STRAT2, STRAT3

load_dotenv()

strategies = [
    STRAT1,
    STRAT2,
    STRAT3,
]


@pytest.mark.parametrize("strategy", strategies)
def test_longevity(strategy):
    assert strategy.longevity > 1 * DAYS


@pytest.mark.parametrize("strategy", strategies)
def test_tvl(strategy):
    assert strategy.tvl >= 0


@pytest.mark.parametrize("strategy", strategies)
def test_describe(strategy):
    info = strategy.describe()
    assert len(info.tokens) > 0
