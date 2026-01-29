from fastapi import APIRouter, HTTPException

from app.models.schemas import ImpactRequest, ImpactResponse, MapNode, MapEdge
from app.services.queries import get_impact

router = APIRouter()

ALLOWED_SCENARIOS = {"supplier_failure", "port_closure"}


@router.post("", response_model=ImpactResponse)
def post_impact(body: ImpactRequest):
    """Return nodes and edges for impact of a disruption (supplier_failure or port_closure)."""
    if body.scenario not in ALLOWED_SCENARIOS:
        raise HTTPException(400, detail=f"scenario must be one of {ALLOWED_SCENARIOS}")
    nodes, edges = get_impact(body.scenario, body.target_id)
    return ImpactResponse(
        nodes=[MapNode(**n) for n in nodes],
        edges=[MapEdge(**e) for e in edges],
    )
