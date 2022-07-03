from fastapi import APIRouter, HTTPException
from sqlmodel import Session

from src.models import StrategyAllocation, create_id
from src.services.fastapi.db import engine

router = APIRouter()


@router.get("/median-score")
def get_median_score_allocation(chain_id: int, address: str, debtToAdd: float = None):
    """Fetch the recommended debt allocation for a given product, using the median-score method"""
    method = "median-score"
    with Session(engine) as session:
        strategy_id = create_id(address, chain_id)
        allocation_id = method + '_' + strategy_id
        allocation = session.get(StrategyAllocation, allocation_id)
        if allocation is None:
            raise HTTPException(
                status_code=404, detail="Allocation for strategy not found"
            )
        strategy = allocation.strategy
        riskGroup = allocation.riskGroup

    # verify input value if provided
    if debtToAdd is not None:
        return debtToAdd < allocation.availableTVL

    return {
        "network": strategy.network,
        "address": strategy.address,
        "name": strategy.name,
        "riskGroup": riskGroup.label,
        "currentTVL": allocation.currentTVL,
        "availableTVL": allocation.availableTVL,
    }
