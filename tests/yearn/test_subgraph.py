import pytest
from dotenv import load_dotenv

from src.yearn import Network, Subgraph, Yearn

load_dotenv()

YEARN_MAINNET = Yearn(Network.Mainnet)
VLT_USDC_VAULT = [
    vault
    for vault in YEARN_MAINNET.vaults
    if vault.address == "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
][0]

YEARN_FANTOM = Yearn(Network.Fantom)
CRV_VAULT = [
    vault
    for vault in YEARN_FANTOM.vaults
    if vault.address == "0x0446acaB3e0242fCf33Aa526f1c95a88068d5042"
][0]


@pytest.mark.parametrize("vault", [VLT_USDC_VAULT, CRV_VAULT])
@pytest.mark.parametrize("num_accounts", [10, 20])
def test_top_wallets(vault, num_accounts):
    subgraph = Subgraph(vault.network)
    wallets = subgraph.top_wallets(vault, num_accounts)
    assert len(wallets) == num_accounts
