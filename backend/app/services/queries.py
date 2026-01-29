"""Cypher queries for supply chain and impact. Return dicts suitable for Pydantic models."""
from app.database import get_driver


def _node_to_map_node(record) -> dict:
    """Build MapNode-like dict from a Neo4j node (record['node'] or record['n'])."""
    node = record.get("node") or record.get("n")
    if node is None:
        raise ValueError("Record has no 'node' or 'n'")
    labels = list(node.labels) if hasattr(node, "labels") else []
    node_type = labels[0] if labels else "Unknown"
    return {
        "id": node.get("id") or "",
        "name": node.get("name") or "",
        "type": node_type,
        "tier": node.get("tier"),
        "lat": node.get("lat"),
        "lon": node.get("lon"),
    }


def _rel_to_map_edge(record) -> dict:
    """Build MapEdge-like dict from a Neo4j relationship (record['r'])."""
    r = record.get("r")
    if r is None:
        raise ValueError("Record has no 'r'")
    start = r.start_node
    end = r.end_node
    start_id = start.get("id") if hasattr(start, "get") else None
    end_id = end.get("id") if hasattr(end, "get") else None
    rel_type = type(r).__name__ if hasattr(r, "__name__") else str(r.type)
    if hasattr(r, "type"):
        rel_type = r.type
    return {
        "from_id": start_id or "",
        "to_id": end_id or "",
        "type": rel_type,
    }


def list_companies() -> list[dict]:
    """Return all companies for dropdowns."""
    driver = get_driver()
    q = """
    MATCH (c:Company)
    RETURN c.id AS id, c.name AS name, c.lat AS lat, c.lon AS lon
    ORDER BY c.name
    """
    with driver.session() as session:
        result = session.run(q)
        return [dict(record) for record in result]


def list_suppliers() -> list[dict]:
    """Return all suppliers for impact target dropdown."""
    driver = get_driver()
    q = "MATCH (s:Supplier) RETURN s.id AS id, s.name AS name ORDER BY s.name"
    with driver.session() as session:
        result = session.run(q)
        return [dict(record) for record in result]


def list_ports() -> list[dict]:
    """Return all ports for impact target dropdown."""
    driver = get_driver()
    q = "MATCH (p:Port) RETURN p.id AS id, p.name AS name ORDER BY p.name"
    with driver.session() as session:
        result = session.run(q)
        return [dict(record) for record in result]


def get_supply_chain(company_id: str, depth: int) -> tuple[list[dict], list[dict]]:
    """Return (nodes, edges) for supply chain: company + upstream via SUPPLIES_TO up to depth.
    Includes LOCATED_IN and SHIPS_VIA for map context.
    """
    driver = get_driver()
    # 1) All nodes reachable from company via SUPPLIES_TO (upstream) up to depth
    # 2) From that set, add LOCATED_IN and SHIPS_VIA neighbors (ports, countries)
    nodes_q = """
    MATCH (c:Company { id: $company_id })
    OPTIONAL MATCH path = (c)<-[:SUPPLIES_TO*1..$depth]-(upstream)
    WITH c, collect(DISTINCT path) AS paths
    UNWIND paths AS p
    UNWIND CASE WHEN p IS NOT NULL THEN nodes(p) ELSE [] END AS n
    WITH collect(DISTINCT n) + [c] AS baseNodes
    UNWIND baseNodes AS bn
    WITH collect(DISTINCT bn) AS chainNodes
    UNWIND chainNodes AS n
    OPTIONAL MATCH (n)-[:LOCATED_IN]->(country:Country)
    OPTIONAL MATCH (n)-[:SHIPS_VIA]->(port:Port)
    WITH chainNodes + collect(DISTINCT country) + collect(DISTINCT port) AS allNodes
    UNWIND allNodes AS node
    WITH collect(DISTINCT node) AS finalNodes
    UNWIND finalNodes AS node
    WHERE node IS NOT NULL AND node.id IS NOT NULL
    RETURN DISTINCT node
    """
    edges_q = """
    MATCH (c:Company { id: $company_id })
    OPTIONAL MATCH path = (c)<-[:SUPPLIES_TO*1..$depth]-(upstream)
    WITH collect(path) AS paths
    UNWIND paths AS p
    UNWIND CASE WHEN p IS NOT NULL THEN relationships(p) ELSE [] END AS r
    WITH collect(DISTINCT r) AS supplyRels
    UNWIND supplyRels AS r
    WHERE r IS NOT NULL
    RETURN DISTINCT startNode(r).id AS from_id, endNode(r).id AS to_id, type(r) AS type
    UNION
    MATCH (c:Company { id: $company_id })<-[:SUPPLIES_TO*1..$depth]-(upstream)
    WITH collect(DISTINCT upstream) + [c] AS chainNodes
    UNWIND chainNodes AS n
    MATCH (n)-[r:LOCATED_IN|SHIPS_VIA]->(other)
    RETURN DISTINCT startNode(r).id AS from_id, endNode(r).id AS to_id, type(r) AS type
    """
    with driver.session() as session:
        nodes_result = session.run(nodes_q, company_id=company_id, depth=depth)
        nodes = [_node_to_map_node({"node": record["node"]}) for record in nodes_result if record.get("node")]

        edges_result = session.run(edges_q, company_id=company_id, depth=depth)
        edges = [
            {"from_id": r["from_id"] or "", "to_id": r["to_id"] or "", "type": r["type"]}
            for r in edges_result
            if r.get("from_id") and r.get("to_id")
        ]
    return nodes, edges


def get_impact(scenario: str, target_id: str) -> tuple[list[dict], list[dict]]:
    """Return (nodes, edges) for impact: supplier_failure or port_closure."""
    driver = get_driver()
    if scenario == "supplier_failure":
        # Downstream: who this supplier feeds (companies + suppliers)
        nodes_q = """
        MATCH (s:Supplier { id: $target_id })
        OPTIONAL MATCH path = (s)-[:SUPPLIES_TO*1..4]->(downstream)
        WITH s, collect(path) AS paths
        UNWIND paths AS p
        UNWIND CASE WHEN p IS NOT NULL THEN nodes(p) ELSE [] END AS n
        WITH collect(DISTINCT n) + s AS allNodes
        UNWIND allNodes AS node
        WHERE node IS NOT NULL AND node.id IS NOT NULL
        RETURN DISTINCT node
        """
        edges_q = """
        MATCH (s:Supplier { id: $target_id })
        OPTIONAL MATCH path = (s)-[:SUPPLIES_TO*1..4]->(downstream)
        UNWIND collect(path) AS p
        UNWIND CASE WHEN p IS NOT NULL THEN relationships(p) ELSE [] END AS r
        WHERE r IS NOT NULL
        RETURN DISTINCT startNode(r).id AS from_id, endNode(r).id AS to_id, type(r) AS type
        """
    elif scenario == "port_closure":
        # Who ships via this port; downstream impact
        nodes_q = """
        MATCH (p:Port { id: $target_id })
        OPTIONAL MATCH (origin)-[:SHIPS_VIA*1..2]->(p)
        WHERE origin:Supplier OR origin:Factory
        OPTIONAL MATCH path = (origin)-[:SUPPLIES_TO|DEPENDS_ON*0..4]->(downstream)
        WITH p, collect(DISTINCT origin) AS origins, collect(path) AS paths
        UNWIND paths AS path
        UNWIND CASE WHEN path IS NOT NULL THEN nodes(path) ELSE [] END AS n
        WITH [p] + origins + collect(DISTINCT n) AS allNodes
        UNWIND allNodes AS node
        WHERE node IS NOT NULL AND node.id IS NOT NULL
        RETURN DISTINCT node
        """
        edges_q = """
        MATCH (p:Port { id: $target_id })<-[:SHIPS_VIA]-(origin)
        WHERE origin:Supplier OR origin:Factory
        OPTIONAL MATCH path = (origin)-[r:SUPPLIES_TO|DEPENDS_ON*1..4]->()
        WITH collect(path) AS paths
        UNWIND paths AS path
        UNWIND CASE WHEN path IS NOT NULL THEN relationships(path) ELSE [] END AS r
        WHERE r IS NOT NULL
        RETURN DISTINCT startNode(r).id AS from_id, endNode(r).id AS to_id, type(r) AS type
        UNION
        MATCH (origin)-[r:SHIPS_VIA]->(p:Port { id: $target_id })
        RETURN DISTINCT startNode(r).id AS from_id, endNode(r).id AS to_id, type(r) AS type
        """
    else:
        return [], []

    with driver.session() as session:
        nodes_result = session.run(nodes_q, target_id=target_id)
        nodes = [_node_to_map_node({"node": record["node"]}) for record in nodes_result if record.get("node")]

        edges_result = session.run(edges_q, target_id=target_id)
        edges = [
            {"from_id": r["from_id"] or "", "to_id": r["to_id"] or "", "type": r["type"]}
            for r in edges_result
            if r.get("from_id") and r.get("to_id")
        ]
    return nodes, edges
