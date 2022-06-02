import json

import pytest
from dotenv import load_dotenv

from src.risk_framework import RiskAnalysis

from .tst_risk_framework_constants import (
    CRV3_VAULT,
    CRV_VAULT,
    STRAT1,
    STRAT2,
    STRAT3,
    USDC_VAULT,
)

load_dotenv()


risk = RiskAnalysis()


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2, STRAT3])
def test_strategy_scores(strategy):
    scores = risk.scores(strategy)
    assert hasattr(scores, "longevityImpact")


@pytest.mark.parametrize("vault", [USDC_VAULT, CRV_VAULT, CRV3_VAULT])
def test_vault_scores(vault):
    scores = risk.scores(vault)
    assert not hasattr(scores, "longevityImpact")
    assert hasattr(scores, "auditScore")


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2, STRAT3])
def test_strategy_describe(strategy):
    info = json.loads(risk.describe(strategy))
    assert len(info["tokens"]) > 1


@pytest.mark.parametrize("vault", [USDC_VAULT, CRV_VAULT, CRV3_VAULT])
def test_vault_describe(vault):
    info = json.loads(risk.describe(vault))
    assert len(info["tokens"]) > 1
    assert len(info["topWallets"]) == 10
