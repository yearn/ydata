import time
from typing import Union, NamedTuple
from decimal import Decimal

from ..utils.web3 import call
from ..utils.price import get_usdc_price
from ..yearn.vaults import Vault


class StrategyParams(NamedTuple):
    performanceFee: Decimal  # Strategist's fee (basis points)
    activation: Decimal  # Activation block.timestamp
    debtRatio: Decimal  # Maximum borrow amount (in BPS of total assets)
    minDebtPerHarvest: Decimal  # Lower limit on the increase of debt since last harvest
    maxDebtPerHarvest: Decimal  # Upper limit on the increase of debt since last harvest
    lastReport: Decimal  # block.timestamp of the last time a report occured
    totalDebt: Decimal  # Total outstanding debt that Strategy has
    totalGain: Decimal  # Total returns that Strategy has realized for Vault
    totalLoss: Decimal  # Total losses that Strategy has realized for Vault


class Strategy:
    address: str
    name: str
    vault: Union[Vault, None]

    """
    Contains strategy-level information
    """

    def __init__(self, address: str, name: str):
        self.address = address
        self.name = name
        self.vault = None

    def __repr__(self):
        return f"<Strategy name={self.name}>"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    @property
    def longevity(self):
        if self.vault is None:
            vault_address = call(self.address, "vault")
        else:
            vault_address = self.vault.address
        params = StrategyParams(*call(vault_address, "strategies", self.address))
        return time.time() - params.activation

    @property
    def tvl(self):
        if self.vault is None:
            vault_address = call(self.address, "vault")
            decimals = Decimal(call(vault_address, "decimals"))
            token_address = call(vault_address, "token")
        else:
            decimals = self.vault.token.decimals
            token_address = self.vault.token.address

        total_assets = Decimal(call(self.address, "estimatedTotalAssets"))
        total_assets /= 10**decimals
        usdc_price = get_usdc_price(token_address)
        return total_assets * usdc_price
