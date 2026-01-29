from typing import Optional

from pydantic import BaseModel, Field


class CompanyOut(BaseModel):
    id: str
    name: str
    lat: Optional[float] = None
    lon: Optional[float] = None


class MapNode(BaseModel):
    id: str
    name: str
    type: str = Field(description="Node label: Company, Supplier, Factory, Port, Country")
    tier: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class MapEdge(BaseModel):
    from_id: str
    to_id: str
    type: str = Field(description="Relationship type: SUPPLIES_TO, DEPENDS_ON, SHIPS_VIA, LOCATED_IN")


class SupplyChainRequest(BaseModel):
    company_id: str
    depth: int = Field(default=4, ge=1, le=4)


class SupplyChainResponse(BaseModel):
    nodes: list[MapNode]
    edges: list[MapEdge]


class ImpactRequest(BaseModel):
    scenario: str = Field(description="supplier_failure or port_closure")
    target_id: str


class ImpactResponse(BaseModel):
    nodes: list[MapNode]
    edges: list[MapEdge]
