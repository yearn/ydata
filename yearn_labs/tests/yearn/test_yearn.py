from ...yearn import Yearn


def test_load_vaults():
    yearn = Yearn()
    assert len(yearn.vaults) > 0


def test_load_strategies():
    yearn = Yearn()
    assert len(yearn.strategies) > 0
