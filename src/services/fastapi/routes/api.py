from enum import Enum

from fastapi import APIRouter
from fastapi.responses import RedirectResponse, Response

from src.services.fastapi.routes import allocation, riskgroups, strategies, vaults


class Tags(Enum):
    vaults = "Vaults"
    strategies = "Strategies"
    riskGroups = "Risk Groups"
    allocation = "Debt Allocation"


router = APIRouter()
router.include_router(vaults.router, tags=[Tags.vaults], prefix="/api/vaults")
router.include_router(
    strategies.router, tags=[Tags.strategies], prefix="/api/strategies"
)
router.include_router(
    riskgroups.router, tags=[Tags.riskGroups], prefix="/api/riskgroups"
)
router.include_router(
    allocation.router, tags=[Tags.allocation], prefix="/api/allocation"
)


@router.get("/", include_in_schema=False)
def root():
    message = """

    Welcome to Yearn Data Analytics!

    The current endpoint for the risk framework API is /api,
    which will automatically redirect you to the API documentation page.

    """
    return Response(content=message, media_type="text/plain")


@router.get("/api", include_in_schema=False)
def redirect_api_docs():
    """Redirect to the OpenAPI documentation"""
    return RedirectResponse("/docs")
