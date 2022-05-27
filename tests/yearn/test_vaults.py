import pytest
from dotenv import load_dotenv
from src.yearn import Network, Yearn

load_dotenv()

yearn = Yearn(Network.Mainnet)
USDC_VAULT = [
    vault
    for vault in yearn.vaults
    if vault.address == "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
][0]
yearn = Yearn(Network.Fantom)
CRV_VAULT = [
    vault
    for vault in yearn.vaults
    if vault.address == "0x0446acaB3e0242fCf33Aa526f1c95a88068d5042"
][0]


@pytest.mark.parametrize("vault", [USDC_VAULT, CRV_VAULT])
def test_wallets(vault):
    wallets = vault.wallets
    assert len(wallets) > 0


@pytest.mark.parametrize("vault", [USDC_VAULT, CRV_VAULT])
def test_describe(vault):
    info = vault.describe()
    assert len(info.topWallets) == 10
