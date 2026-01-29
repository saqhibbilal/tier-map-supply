from fastapi import APIRouter
from app.services.queries import list_ports

router = APIRouter()


@router.get("", response_model=list[dict])
def get_ports():
    """List ports for impact target dropdown."""
    return list_ports()
