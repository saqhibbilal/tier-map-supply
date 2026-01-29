from fastapi import APIRouter
from app.services.queries import list_suppliers

router = APIRouter()


@router.get("", response_model=list[dict])
def get_suppliers():
    """List suppliers for impact target dropdown."""
    return list_suppliers()
