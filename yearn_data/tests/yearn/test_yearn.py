import pytest

from ...yearn import Yearn, Strategy
from ...risk.framework import RiskFrameworkScores

GENLEVCOMP_V3 = Strategy(
    "0x1676055fE954EE6fc388F9096210E5EbE0A9070c", "GenLevCompV3", RiskFrameworkScores()
)
SSC_DAI_IB = Strategy(
    "0x3280499298ACe3FD3cd9C2558e9e8746ACE3E52d", "ssc_dai_ib", RiskFrameworkScores()
)

yearn = Yearn()

DAI_VAULT = [
    vault
    for vault in yearn.vaults
    if vault.address == "0xdA816459F1AB5631232FE5e97a05BBBb94970c95"
][0]


def test_load_vaults():
    assert len(yearn.vaults) > 0


def test_load_strategies():
    assert len(yearn.strategies) > 0


@pytest.mark.parametrize("name", ["GenLevCompV3", "ssc_dai_ib"])
def test_get_framework_scores(name):
    scores = yearn.get_framework_scores(name)
    assert hasattr(scores, 'auditScore')


@pytest.mark.parametrize("strategy", [GENLEVCOMP_V3, SSC_DAI_IB])
def test_describe_strategy(strategy):
    info = yearn.describe(strategy)
    assert 'Maker' in [protocol['Name'] for protocol in info.protocols]


@pytest.mark.parametrize("vault", [DAI_VAULT])
def test_describe_vault(vault):
    info = yearn.describe(vault)
    assert 'Maker' in [protocol['Name'] for protocol in info.protocols]
    assert len(info.top_wallets) == 10
