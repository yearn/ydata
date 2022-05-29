import pytest
import json
from dotenv import load_dotenv

from src.yearn import Network, Strategy, Yearn
from src.risk_framework import RiskAnalysis

load_dotenv()

STRAT1 = Strategy(
    Network.Mainnet, "0x1676055fE954EE6fc388F9096210E5EbE0A9070c", "GenLevCompV3"
)
STRAT2 = Strategy(
    Network.Fantom,
    "0x695A4a6e5888934828Cb97A3a7ADbfc71A70922D",
    "StrategyLenderYieldOptimiser",
)
yearn = Yearn(Network.Mainnet)
USDC_VAULT = [
    vault
    for vault in yearn.vaults
    if vault.address == "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
][0]
yearn = Yearn(Network.Fantom)
CRV_VAULT = [
    vault
    for vault in yearn.vaults
    if vault.address == "0x0446acaB3e0242fCf33Aa526f1c95a88068d5042"
][0]

risk = RiskAnalysis()


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2])
def test_strategy_scores(strategy):
    scores = risk.scores(strategy)
    assert hasattr(scores, "longevityImpact")


@pytest.mark.parametrize("vault", [USDC_VAULT, CRV_VAULT])
def test_vault_scores(vault):
    scores = risk.scores(vault)
    assert not hasattr(scores, "longevityImpact")
    assert hasattr(scores, "auditScore")


@pytest.mark.parametrize("strategy", [STRAT1, STRAT2])
def test_strategy_describe(strategy):
    info = json.loads(risk.describe(strategy))
    assert len(info["tokens"]) > 1


@pytest.mark.parametrize("vault", [USDC_VAULT, CRV_VAULT])
def test_vault_describe(vault):
    info = json.loads(risk.describe(vault))
    assert len(info["tokens"]) > 1
    assert len(info["topWallets"]) == 10
