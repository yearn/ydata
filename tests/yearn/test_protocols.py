from src.yearn.protocols import Protocol, ProtocolList
from .tst_yearn_constants import AAVE_V3,AAVE_V2


def test_aave_match():
    assert AAVE_V3 == "aave"
    assert AAVE_V3 == "aave v3"
    assert AAVE_V2 != "aave v3"
    assert AAVE_V2 == "aave v2"
    assert AAVE_V3 != "aave v2"


def test_protocol_match():
    assert Protocol("Compound Finance") == "compound"
    assert Protocol("88mph") == "88mph v3.0"
    assert Protocol("Fei Protocol") == "fei"
    assert Protocol("Curve.fi") != "curve"
    assert Protocol("Lido") == "Lido Finance"
    assert Protocol("veDAO") == "veDAO"
    assert Protocol("veDAO") != "Aave"


def test_protocols():
    assert any([protocol == "uniswap" for protocol in ProtocolList])
    assert any([protocol == "maker" for protocol in ProtocolList])
    assert any([protocol == "curve" for protocol in ProtocolList])
