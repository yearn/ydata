import pytest
from ...risk.defi_safety import DeFiSafety

protocols = ["yearn", "uniswap"]

defi_safety = DeFiSafety()


@pytest.mark.parametrize("protocol", protocols)
def test_protocols(protocol):
    assert any([protocol in name.lower() for name in defi_safety.protocols])


@pytest.mark.parametrize("protocol", protocols)
def test_scores(protocol):
    assert len(defi_safety.scores(protocol)) > 0
