import pytest
from dotenv import load_dotenv
from .tst_yearn_constants import STRAT1, STRAT2, DAYS

load_dotenv()


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2])
def test_longevity(strategy):
    assert strategy.longevity > 30 * DAYS


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2])
def test_tvl(strategy):
    assert strategy.tvl >= 0


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2])
def test_describe(strategy):
    info = strategy.describe()
    assert any(["yv" in token for token in info.tokens])
