import json
import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response
from sqlmodel import Session, create_engine, select

from src.models import RiskGroup, Strategy, Vault, create_id

load_dotenv()

engine = create_engine(os.environ["DATABASE_URI"])
app = FastAPI()


class Tags(Enum):
    vaults = "Vaults"
    strategies = "Strategies"
    riskGroups = "Risk Groups"


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


@app.get("/api/vaults/{chain_id}", tags=[Tags.vaults])
def get_network_vaults(chain_id):
    """Fetch vault-level risk metrics for a specific chain"""
    with Session(engine) as session:
        query = select(Vault).where(Vault.network == chain_id)
        vaults = session.exec(query).all()
    return {vault.address: json.loads(vault.info) for vault in vaults}


@app.get("/api/vaults/{chain_id}/{address}", tags=[Tags.vaults])
def get_vault(chain_id, address):
    """Fetch vault-level risk metrics for a specific vault"""
    with Session(engine) as session:
        vault_id = create_id(address, chain_id)
        vault = session.get(Vault, vault_id)
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


@app.get("/api/strategies/{chain_id}", tags=[Tags.strategies])
def get_network_strategies(chain_id):
    """Fetch strategy-level risk metrics for a specific chain"""
    with Session(engine) as session:
        query = select(Strategy).where(Strategy.network == chain_id)
        strategies = session.exec(query).all()
    return {strategy.address: json.loads(strategy.info) for strategy in strategies}


@app.get("/api/strategies/{chain_id}/{address}", tags=[Tags.strategies])
def get_strategy(chain_id, address):
    """Fetch strategy-level risk metrics for a specific strategy"""
    with Session(engine) as session:
        strategy_id = create_id(address, chain_id)
        strategy = session.get(Strategy, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return json.loads(strategy.info)


@app.get("/api/riskgroups", tags=[Tags.riskGroups])
def get_all_risk_groups():
    """Fetch all risk groups"""
    with Session(engine) as session:
        query = select(RiskGroup)
        groups = session.exec(query).all()
    return groups


@app.get("/api/riskgroups/{group_id}", tags=[Tags.riskGroups])
def get_risk_group(group_id):
    """Fetch a specific risk group"""
    with Session(engine) as session:
        group = session.get(RiskGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group ID not found")
    return group
