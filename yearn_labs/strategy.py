class Strategy:
    """
    Contains strategy-level information
    """

    def __init__(self, address: str, name: str):
        self.address = address
        self.name = name

    def __repr__(self):
        return f"Strategy({self.name})"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)
