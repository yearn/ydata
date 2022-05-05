import pytest
from ...yearn import Yearn

yearn = Yearn()


def test_load_vaults():
    assert len(yearn.vaults) > 0


def test_load_strategies():
    assert len(yearn.strategies) > 0


@pytest.mark.parametrize("name", ["GenLevCompV3", "ssc_dai_ib"])
def test_get_strategy_scores(name):
    scores = yearn.get_strategy_scores(name)
    assert hasattr(scores, 'auditScore')
