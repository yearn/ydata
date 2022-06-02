import pytest
from dotenv import load_dotenv

from src.yearn import Subgraph

from .tst_yearn_constants import CRV_VAULT, VLT_CRV3_VAULT, VLT_USDC_VAULT

load_dotenv()


@pytest.mark.parametrize("vault", [VLT_USDC_VAULT, CRV_VAULT, VLT_CRV3_VAULT])
@pytest.mark.parametrize("num_accounts", [10, 20])
def test_top_wallets(vault, num_accounts):
    subgraph = Subgraph(vault.network)
    wallets = subgraph.top_wallets(vault, num_accounts)
    assert len(wallets) == num_accounts
