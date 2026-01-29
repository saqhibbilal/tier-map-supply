import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import SupplyChainRequest, SupplyChainResponse, MapNode, MapEdge
from app.services.queries import get_supply_chain

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=SupplyChainResponse)
def post_supply_chain(body: SupplyChainRequest):
    """Return nodes and edges for the supply chain (company + upstream) up to given depth."""
    try:
        nodes, edges = get_supply_chain(body.company_id, body.depth)
        return SupplyChainResponse(
            nodes=[MapNode(**n) for n in nodes],
            edges=[MapEdge(**e) for e in edges],
        )
    except Exception as e:
        logger.exception("Supply chain error")
        raise HTTPException(status_code=500, detail=str(e))
