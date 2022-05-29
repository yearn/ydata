import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import create_engine, Session, select

from src.models import Vault, Strategy

engine = create_engine(os.environ["DATABASE_URI"])
app = FastAPI()


@app.get("/api")
def redirect_API_root():
    """Redirect to the OpenAPI documentation"""
    return RedirectResponse("/docs")


@app.get("/api/vaults")
def get_all_vaults():
    """Fetch vault-level risk metrics for all available vaults"""
    with Session(engine) as session:
        query = select(Vault)
        vaults = session.exec(query).all()
    return {vault.address: json.loads(vault.info) for vault in vaults}


@app.get("/api/vaults/{address}")
def get_vault(address):
    """Fetch vault-level risk metrics for a specific vault"""
    with Session(engine) as session:
        vault = session.get(Vault, address.lower())
    if vault is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return json.loads(vault.info)


@app.get("/api/strategies")
def get_all_strategies():
    """Fetch strategy-level risk metrics for all available strategies"""
    with Session(engine) as session:
        query = select(Strategy)
        strategies = session.exec(query).all()
    return {strategy.address: json.loads(strategy.info) for strategy in strategies}


@app.get("/api/strategies/{address}")
def get_strategy(address):
    """Fetch strategy-level risk metrics for a specific strategy"""
    with Session(engine) as session:
        strategy = session.get(Strategy, address.lower())
    if strategy is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return json.loads(strategy.info)
