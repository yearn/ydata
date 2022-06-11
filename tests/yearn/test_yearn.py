import os
import pytest
from dotenv import load_dotenv

from ..constants import YEARN_ARBITRUM, YEARN_FANTOM, YEARN_MAINNET
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

yearn_chains = [
    YEARN_MAINNET,
    YEARN_FANTOM,
    YEARN_ARBITRUM,
]


@pytest.mark.parametrize("yearn", yearn_chains)
def test_load_vaults(yearn):
    assert len(yearn.vaults) > 0


@pytest.mark.parametrize("yearn", yearn_chains)
def test_load_strategies(yearn):
    assert len(yearn.strategies) > 0
