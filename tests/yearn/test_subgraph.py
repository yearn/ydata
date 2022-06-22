import os

import pytest
from dotenv import load_dotenv

from src.utils.web3 import Web3Provider
from src.yearn import Subgraph
from tests.constants import CRV3_VAULT, CRV_VAULT, USDC_VAULT

BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

vaults = [USDC_VAULT, CRV_VAULT, CRV3_VAULT]


@pytest.mark.parametrize("vault", vaults)
@pytest.mark.parametrize("num_accounts", [10, 20])
def test_top_wallets(vault, num_accounts):
    subgraph = Subgraph(vault.network)
    wallets = subgraph.top_wallets(vault, num_accounts)
    assert len(wallets) == num_accounts


@pytest.mark.parametrize("transfer_type", ["deposits", "withdrawals"])
@pytest.mark.parametrize("vault", vaults)
@pytest.mark.parametrize("num_blocks", [100_000])
def test_transfers(transfer_type, vault, num_blocks):
    w3 = Web3Provider(vault.network)
    current_block = w3.provider.eth.get_block_number()
    from_block = current_block - num_blocks

    subgraph = Subgraph(vault.network)
    transfers = subgraph.transfers(
        transfer_type, vault, from_block=from_block, to_block=current_block
    )
    assert transfers.count >= 0
    assert transfers.shares >= 0

    if account_shares := transfers.account_transfers:
        account_share = next(iter(account_shares.items()))[1]
        assert account_share.count >= 0
        assert account_share.shares >= 0
