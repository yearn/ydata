import os
import pytest
import pandas as pd

from ...yearn import Strategy
from ...risk.framework import RiskFrameworkScores

GENLEVCOMP_V3 = Strategy(
    "0x1676055fE954EE6fc388F9096210E5EbE0A9070c", "GenLevCompV3", RiskFrameworkScores()
)
SSC_DAI_IB = Strategy(
    "0x3280499298ACe3FD3cd9C2558e9e8746ACE3E52d", "ssc_dai_ib", RiskFrameworkScores()
)
DAYS = 60 * 60 * 24

sample_path = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'data', 'sample_risk_weights.csv'
)
sample_weights = pd.read_csv(sample_path, header=0)


@pytest.mark.parametrize("strategy", [GENLEVCOMP_V3, SSC_DAI_IB])
def test_longevity(strategy):
    assert strategy.longevity > 30 * DAYS


@pytest.mark.parametrize("strategy", [GENLEVCOMP_V3, SSC_DAI_IB])
def test_tvl(strategy):
    assert strategy.tvl > 0


@pytest.mark.parametrize("strategy", [GENLEVCOMP_V3, SSC_DAI_IB])
def test_risk_scores(strategy):
    assert hasattr(strategy.risk_scores, "longevityImpact")


@pytest.mark.parametrize("strategy", [GENLEVCOMP_V3, SSC_DAI_IB])
def test_risk_score(strategy):
    score = strategy.risk_score()
    assert score.low == score.high
    score = strategy.risk_score(sample_weights)
    assert score.low <= score.high


@pytest.mark.parametrize("strategy", [GENLEVCOMP_V3, SSC_DAI_IB])
def test_describe(strategy):
    info = strategy.describe()
    assert 'Maker' in info.protocols
    assert 'DAI' in info.tokens
