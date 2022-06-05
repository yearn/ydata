import json

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from src.models import Strategy, create_id
from src.services.fastapi.db import engine

router = APIRouter()


@router.get("/")
def get_all_strategies():
    """Fetch strategy-level risk metrics for all available strategies"""
    with Session(engine) as session:
        query = select(Strategy)
        strategies = session.exec(query).all()
    return {strategy.address: json.loads(strategy.info) for strategy in strategies}


@router.get("/{chain_id}")
def get_network_strategies(chain_id):
    """Fetch strategy-level risk metrics for a specific chain"""
    with Session(engine) as session:
        query = select(Strategy).where(Strategy.network == chain_id)
        strategies = session.exec(query).all()
    return {strategy.address: json.loads(strategy.info) for strategy in strategies}


@router.get("/{chain_id}/{address}")
def get_strategy(chain_id, address):
    """Fetch strategy-level risk metrics for a specific strategy"""
    with Session(engine) as session:
        strategy_id = create_id(address, chain_id)
        strategy = session.get(Strategy, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return json.loads(strategy.info)
