import os
import pytest
import pandas as pd

from ...yearn import Yearn

yearn = Yearn()

USDC_VAULT = [
    vault
    for vault in yearn.vaults
    if vault.address == "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
][0]
DAI_VAULT = [
    vault
    for vault in yearn.vaults
    if vault.address == "0xdA816459F1AB5631232FE5e97a05BBBb94970c95"
][0]

sample_path = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'data', 'sample_risk_weights.csv'
)
sample_weights = pd.read_csv(sample_path, header=0)


@pytest.mark.parametrize("vault", [USDC_VAULT, DAI_VAULT])
def test_risk_scores(vault):
    assert hasattr(vault.risk_scores, "auditScore")


@pytest.mark.parametrize("vault", [USDC_VAULT, DAI_VAULT])
def test_risk_score(vault):
    score = vault.risk_score()
    assert score.low == score.high
    score = vault.risk_score(sample_weights)
    assert score.low <= score.high


@pytest.mark.parametrize("vault", [USDC_VAULT, DAI_VAULT])
def test_wallets(vault):
    wallets = vault.wallets
    assert len(wallets) > 0


@pytest.mark.parametrize("vault", [USDC_VAULT, DAI_VAULT])
def test_describe(vault):
    info = vault.describe()
    assert 'Maker' in [protocol['Name'] for protocol in info.protocols]
    assert 'DAI' in [token['Name'] for token in info.tokens]
    assert len(info.topWallets) == 10
