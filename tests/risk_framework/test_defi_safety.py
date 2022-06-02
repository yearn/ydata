import pytest

from src.risk_framework.defi_safety import DeFiSafety
from src.yearn.protocols import Protocol

defi_safety = DeFiSafety()


@pytest.mark.parametrize("protocol", [Protocol('Aave'), Protocol('1inch')])
def test_scores(protocol):
    assert (
        defi_safety.scores(protocol) is not None
    ), f"{protocol.name} missing from DeFi Safety"
