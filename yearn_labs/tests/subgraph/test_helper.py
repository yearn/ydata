import os
import pytest
from ...subgraph import SubgraphHelper
from dotenv import load_dotenv

load_dotenv()

VAULT1_ADDRESS = "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
VAULT1_NAME = "USDC yVault"
VAULT2_ADDRESS = "0xdA816459F1AB5631232FE5e97a05BBBb94970c95"
VAULT2_NAME = "DAI yVault"

STRAT1_ADDRESS = "0x3280499298ACe3FD3cd9C2558e9e8746ACE3E52d"
STRAT1_NAME = "GenLevCompV3"
STRAT2_ADDRESS = "0xa6D1C610B3000F143c18c75D84BaA0eC22681185"
STRAT2_NAME = "ssc"


def make_params(*args):
    return [*args, list(args)]


vault_addresses = make_params(VAULT1_ADDRESS, VAULT2_ADDRESS)
vault_names = make_params(VAULT1_NAME, VAULT2_NAME)
strategy_addresses = make_params(STRAT1_ADDRESS, STRAT2_ADDRESS)
strategy_names = make_params(STRAT1_NAME, STRAT2_NAME)

helper = SubgraphHelper(url=os.environ["SUBGRAPH_URL"])


def test_get_vaults_all():
    result = helper.get_vaults()
    assert len(result) > 0


@pytest.mark.parametrize("vault_address", vault_addresses)
def test_get_vaults_from_address(vault_address):
    result = helper.get_vaults({"address": vault_address})
    assert len(result) > 0


@pytest.mark.parametrize("vault_name", vault_names)
def test_get_vaults_from_name(vault_name):
    result = helper.get_vaults({"nameLike": vault_name})
    assert len(result) > 0


def test_get_strategies_all():
    result = helper.get_strategies()
    assert len(result) > 0


@pytest.mark.parametrize("vault_address", vault_addresses)
def test_get_strategies_from_vault_address(vault_address):
    result = helper.get_strategies({"vaultAddress": vault_address})
    assert len(result) > 0


@pytest.mark.parametrize("vault_name", vault_names)
def test_get_strategies_from_vault_name(vault_name):
    result = helper.get_strategies({"vaultName": vault_name})
    assert len(result) > 0


@pytest.mark.parametrize("strategy_address", strategy_addresses)
def test_get_strategies_from_address(strategy_address):
    result = helper.get_strategies({"address": strategy_address})
    assert len(result) > 0


@pytest.mark.parametrize("strategy_name", strategy_names)
def test_get_strategies_from_name(strategy_name):
    result = helper.get_strategies({"nameLike": strategy_name})
    assert len(result) > 0
