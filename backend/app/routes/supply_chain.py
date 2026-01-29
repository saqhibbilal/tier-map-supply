from fastapi import APIRouter, HTTPException

from app.models.schemas import SupplyChainRequest, SupplyChainResponse, MapNode, MapEdge
from app.services.queries import get_supply_chain

router = APIRouter()


@router.post("", response_model=SupplyChainResponse)
def post_supply_chain(body: SupplyChainRequest):
    """Return nodes and edges for the supply chain (company + upstream) up to given depth."""
    nodes, edges = get_supply_chain(body.company_id, body.depth)
    return SupplyChainResponse(
        nodes=[MapNode(**n) for n in nodes],
        edges=[MapEdge(**e) for e in edges],
    )
