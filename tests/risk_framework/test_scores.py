import os
import pytest
import pandas as pd
from src.risk_framework.scores import StrategyRiskScores, VaultRiskScores


STRAT_SCORE = StrategyRiskScores(1, 2, 1, 2, 1, 2, 1, 2)
VAULT_SCORE = VaultRiskScores(1, 1, 1, 1, 1, 5)

file_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "src", "risk_framework", "weights.csv"
)
weights = pd.read_csv(file_path, header=0)


@pytest.mark.parametrize("strategy_scores", [STRAT_SCORE])
def test_strategy_profile(strategy_scores):
    score_uniform = strategy_scores.profile()
    assert score_uniform.low <= score_uniform.high

    score_weighted = strategy_scores.profile(weights)
    assert score_weighted.low <= score_weighted.high
    assert score_uniform != score_weighted


@pytest.mark.parametrize("vault_scores", [VAULT_SCORE])
def test_vault_profile(vault_scores):
    score_uniform = vault_scores.profile()
    assert score_uniform.low <= score_uniform.high

    score_weighted = vault_scores.profile(weights)
    assert score_weighted.low <= score_weighted.high
    assert score_uniform != score_weighted
