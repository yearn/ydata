import pytest
from src.yearn.protocols import ProtocolList
from src.risk_framework.defi_safety import DeFiSafety


defi_safety = DeFiSafety()


@pytest.mark.parametrize("protocol", ProtocolList)
def test_scores(protocol):
    assert (
        defi_safety.scores(protocol) is not None
    ), f"{protocol.name} missing from DeFi Safety"
