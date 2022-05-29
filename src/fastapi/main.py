import os
import json
from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response
from sqlmodel import create_engine, Session, select

from src.models import Vault, Strategy

engine = create_engine(os.environ["DATABASE_URI"])
app = FastAPI()


class Tags(Enum):
    vaults = "vaults"
    strategies = "strategies"


@app.get("/", include_in_schema=False)
def root():
    message = """

    Welcome to Yearn Data Analytics!

    The current endpoint for the risk framework API is /api,
    which will automatically redirect you to the API documentation page.

    """
    return Response(content=message, media_type="text/plain")


@app.get("/api", include_in_schema=False)
def redirect_api_docs():
    """Redirect to the OpenAPI documentation"""
    return RedirectResponse("/docs")


@app.get("/api/vaults", tags=[Tags.vaults])
def get_all_vaults():
    """Fetch vault-level risk metrics for all available vaults"""
    with Session(engine) as session:
        query = select(Vault)
        vaults = session.exec(query).all()
    return {vault.address: json.loads(vault.info) for vault in vaults}


@app.get("/api/vaults/{address}", tags=[Tags.vaults])
def get_vault(address):
    """Fetch vault-level risk metrics for a specific vault"""
    with Session(engine) as session:
        vault = session.get(Vault, address.lower())
    if vault is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return json.loads(vault.info)


@app.get("/api/strategies", tags=[Tags.strategies])
def get_all_strategies():
    """Fetch strategy-level risk metrics for all available strategies"""
    with Session(engine) as session:
        query = select(Strategy)
        strategies = session.exec(query).all()
    return {strategy.address: json.loads(strategy.info) for strategy in strategies}


@app.get("/api/strategies/{address}", tags=[Tags.strategies])
def get_strategy(address):
    """Fetch strategy-level risk metrics for a specific strategy"""
    with Session(engine) as session:
        strategy = session.get(Strategy, address.lower())
    if strategy is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return json.loads(strategy.info)
