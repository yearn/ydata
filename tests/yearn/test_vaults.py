import pytest
from dotenv import load_dotenv

from .tst_yearn_constants import CRV_VAULT, VLT_CRV3_VAULT, VLT_USDC_VAULT

load_dotenv()


@pytest.mark.parametrize("vault", [VLT_USDC_VAULT, CRV_VAULT, VLT_CRV3_VAULT])
def test_wallets(vault):
    wallets = vault.wallets
    assert len(wallets) > 0


@pytest.mark.parametrize("vault", [VLT_USDC_VAULT, CRV_VAULT, VLT_CRV3_VAULT])
def test_describe(vault):
    info = vault.describe()
    assert len(info.topWallets) == 10
