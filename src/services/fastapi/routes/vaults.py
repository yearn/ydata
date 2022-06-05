import json

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from src.models import Vault, create_id
from src.services.fastapi.db import engine

router = APIRouter()


@router.get("/")
def get_all_vaults():
    """Fetch vault-level risk metrics for all available vaults"""
    with Session(engine) as session:
        query = select(Vault)
        vaults = session.exec(query).all()
    return {vault.address: json.loads(vault.info) for vault in vaults}


@router.get("/{chain_id}")
def get_network_vaults(chain_id):
    """Fetch vault-level risk metrics for a specific chain"""
    with Session(engine) as session:
        query = select(Vault).where(Vault.network == chain_id)
        vaults = session.exec(query).all()
    return {vault.address: json.loads(vault.info) for vault in vaults}


@router.get("/{chain_id}/{address}")
def get_vault(chain_id, address):
    """Fetch vault-level risk metrics for a specific vault"""
    with Session(engine) as session:
        vault_id = create_id(address, chain_id)
        vault = session.get(Vault, vault_id)
    if vault is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return json.loads(vault.info)
