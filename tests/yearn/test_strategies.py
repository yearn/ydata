import pytest
from dotenv import load_dotenv

from .tst_yearn_constants import DAYS, STRAT1, STRAT2, STRAT3

load_dotenv()


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2, STRAT3])
def test_longevity(strategy):
    assert strategy.longevity > 1 * DAYS


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2, STRAT3])
def test_tvl(strategy):
    assert strategy.tvl >= 0


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2, STRAT3])
def test_describe(strategy):
    info = strategy.describe()
    assert len(info.tokens) > 0
