import os

import pytest
from dotenv import load_dotenv

from src.risk_framework import RiskManager

from ..constants import YEARN_ARBITRUM

BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))


@pytest.mark.parametrize("yearn", [YEARN_ARBITRUM])
def test_median_score_allocation(yearn):
    manager = RiskManager(yearn)
    allocations = manager.median_score_allocation()
    assert len(allocations) == len(yearn.strategies)
