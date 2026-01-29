from fastapi import APIRouter, HTTPException

from app.models.schemas import CompanyOut
from app.services.queries import list_companies

router = APIRouter()


@router.get("", response_model=list[CompanyOut])
def get_companies():
    """List all companies for dropdowns."""
    rows = list_companies()
    if not rows:
        return []
    return [CompanyOut(**r) for r in rows]
