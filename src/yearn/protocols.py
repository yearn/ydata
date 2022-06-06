import re
from typing import List


class Protocol:
    name: str
    include: List[str]
    exclude: List[str]

    """
    Regex matching for protocol names
    """

    def __init__(self, name: str, include: List[str] = [], exclude: List[str] = []):
        self.name = name
        self.include = include + [self.strip(name)]
        self.exclude = exclude

    def strip(self, name):
        name = name.lower()
        name = name.replace("finance", "")
        name = name.replace("protocol", "")
        name = name.replace("dao", "")
        name = name.replace(" ", "")
        return name

    def __eq__(self, other):
        if not (isinstance(other, str) or isinstance(other, Protocol)):
            return False
        if isinstance(other, Protocol):
            other = other.name
        other = self.strip(other)
        if any([re.match(pattern, other) for pattern in self.exclude]):
            return False
        return any([re.match(pattern, other) for pattern in self.include])

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<Protocol name={self.name}>"

    def __hash__(self):
        return hash(self.name)


# List of known protocols
ProtocolList: List[Protocol] = [
    Protocol("0xDAO"),
    Protocol("1inch"),
    Protocol("88mph"),
    Protocol("Aave", exclude=[".*v2"]),
    Protocol("Aave V2", exclude=["aave$"]),
    Protocol("Abracadabra"),
    Protocol("Alpha Homora"),
    Protocol("Angle Protocol"),
    Protocol("Balancer"),
    Protocol("Beethoven-X", include=["beethoven"]),
    Protocol("Compound Finance"),
    Protocol("Convex Finance"),
    Protocol("C.R.E.A.M. Finance", include=["cream"]),
    Protocol("Curve.fi", include=["curve"]),
    Protocol("dYdX"),
    Protocol("Ester Finance"),
    Protocol("Fei Protocol"),
    Protocol("FIAT DAO", include=["fiat"]),
    Protocol("Geist Finance"),
    Protocol("Hector Finance"),
    Protocol("Hegic"),
    Protocol("Idle Finance"),
    Protocol("Inverse Finance"),
    Protocol("Iron Bank"),
    Protocol("KeeperDAO"),
    Protocol("LeagueDAO"),
    Protocol("Lido"),
    Protocol("Liquity"),
    Protocol("MakerDAO"),
    Protocol("Mushrooms Finance", include=["mushroom"]),
    Protocol("Notional Finance"),
    Protocol("Origin Protocol"),
    Protocol("PoolTogether"),
    Protocol("Reflexer"),
    Protocol("Reserve Protocol"),
    Protocol("Scream"),
    Protocol("ShapeShift"),
    Protocol("Solidex Finance"),
    Protocol("SpiritSwap"),
    Protocol("SpookySwap"),
    Protocol("Sushi"),
    Protocol("Synthetix"),
    Protocol("Tarot"),
    Protocol("Tokemak"),
    Protocol("TrustToken"),
    Protocol("Uniswap"),
    Protocol("Universe"),
    Protocol("veDAO", exclude=["ve[a-zA-Z0-9_]*"]),
    Protocol("Vesper Finance"),
    Protocol("Yearn Finance", include=["ygov"]),
]


def get_protocol(name: str) -> Protocol:
    try:
        idx = ProtocolList.index(Protocol(name))
        return ProtocolList[idx]
    except ValueError:
        return Protocol("Unknown Protocol")
