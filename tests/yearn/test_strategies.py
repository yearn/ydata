import pytest
from dotenv import load_dotenv
from src.yearn import Network, Strategy

load_dotenv()

STRAT1 = Strategy(
    Network.Mainnet, "0x1676055fE954EE6fc388F9096210E5EbE0A9070c", "GenLevCompV3"
)
STRAT2 = Strategy(
    Network.Fantom,
    "0x695A4a6e5888934828Cb97A3a7ADbfc71A70922D",
    "StrategyLenderYieldOptimiser",
)
DAYS = 60 * 60 * 24


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
