import os
import pytest
from dotenv import load_dotenv

from ..constants import DAYS, STRAT1, STRAT2, STRAT3
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

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
