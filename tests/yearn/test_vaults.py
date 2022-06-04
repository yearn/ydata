import pytest
from dotenv import load_dotenv

from ..constants import CRV3_VAULT, CRV_VAULT, USDC_VAULT

load_dotenv()

vaults = [USDC_VAULT, CRV_VAULT, CRV3_VAULT]


@pytest.mark.parametrize("vault", vaults)
def test_wallets(vault):
    wallets = vault.wallets
    assert len(wallets) > 0


@pytest.mark.parametrize("vault", vaults)
def test_describe(vault):
    info = vault.describe()
    assert len(info.topWallets) == 10
