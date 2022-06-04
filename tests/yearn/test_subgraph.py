import pytest
from dotenv import load_dotenv

from src.yearn import Subgraph

from ..constants import CRV3_VAULT, CRV_VAULT, USDC_VAULT

load_dotenv()

vaults = [USDC_VAULT, CRV_VAULT, CRV3_VAULT]


@pytest.mark.parametrize("vault", vaults)
@pytest.mark.parametrize("num_accounts", [10, 20])
def test_top_wallets(vault, num_accounts):
    subgraph = Subgraph(vault.network)
    wallets = subgraph.top_wallets(vault, num_accounts)
    assert len(wallets) == num_accounts
