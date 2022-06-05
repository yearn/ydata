from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from src.models import RiskGroup, create_id
from src.services.fastapi.db import engine

router = APIRouter()


@router.get("/")
def get_all_risk_groups():
    """Fetch all risk groups"""
    with Session(engine) as session:
        query = select(RiskGroup)
        groups = session.exec(query).all()
    return groups


@router.get("/{chain_id}")
def get_network_risk_groups(chain_id):
    """Fetch risk groups for a specific chain"""
    with Session(engine) as session:
        query = select(RiskGroup).where(RiskGroup.network == chain_id)
        groups = session.exec(query).all()
    return groups


@router.get("/{chain_id}/{group_id}")
def get_risk_group(chain_id, group_id):
    """Fetch a specific risk group"""
    with Session(engine) as session:
        group_id = create_id(group_id, chain_id)
        group = session.get(RiskGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group ID not found")
    return group
