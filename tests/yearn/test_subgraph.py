import pytest
from dotenv import load_dotenv

from src.yearn.subgraph import Subgraph

from ..constants import CRV3_VAULT, CRV_VAULT, USDC_VAULT

from src.utils.web3 import Web3Provider  # isort:skip


load_dotenv()

vaults = [USDC_VAULT, CRV_VAULT, CRV3_VAULT]


@pytest.mark.parametrize("vault", vaults)
@pytest.mark.parametrize("num_accounts", [10, 20])
def test_top_wallets(vault, num_accounts):
    subgraph = Subgraph(vault.network)
    wallets = subgraph.top_wallets(vault, num_accounts)
    assert len(wallets) == num_accounts


@pytest.mark.parametrize("num_blocks", [1000000])
@pytest.mark.parametrize("vault", vaults)
def test_price_per_share(vault, num_blocks):
    w3 = Web3Provider(vault.network)
    current_block = w3.provider.eth.get_block_number()
    from_block = current_block - num_blocks

    subgraph = Subgraph(vault.network)
    prices = subgraph.price_per_share(vault, from_block)
    assert len(prices) > 0
