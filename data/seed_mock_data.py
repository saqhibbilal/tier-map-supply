#!/usr/bin/env python3
"""
Seed the supply chain graph with mock but realistic data.
Run from project root with Neo4j up: python data/seed_mock_data.py
Uses NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD from .env or environment.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "supplymap-dev")


def run_schema(driver):
    """Apply schema.cypher (constraints and indexes)."""
    schema_path = Path(__file__).parent / "schema.cypher"
    text = schema_path.read_text()
    # Split by semicolon, strip comments and empty lines
    statements = [
        s.strip()
        for s in text.split(";")
        if s.strip() and not s.strip().startswith("//")
    ]
    with driver.session() as session:
        for stmt in statements:
            if stmt:
                session.run(stmt)


def clear_graph(driver):
    """Remove all nodes and relationships (keeps constraints/indexes)."""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


def seed(driver):
    with driver.session() as session:
        # ----- Countries -----
        countries = [
            {"id": "usa", "name": "United States", "code": "US", "lat": 39.8, "lon": -98.6},
            {"id": "chn", "name": "China", "code": "CN", "lat": 35.9, "lon": 104.2},
            {"id": "deu", "name": "Germany", "code": "DE", "lat": 51.2, "lon": 10.5},
            {"id": "jpn", "name": "Japan", "code": "JP", "lat": 36.2, "lon": 138.3},
            {"id": "mex", "name": "Mexico", "code": "MX", "lat": 23.6, "lon": -102.6},
            {"id": "vnm", "name": "Vietnam", "code": "VN", "lat": 14.1, "lon": 108.3},
            {"id": "nld", "name": "Netherlands", "code": "NL", "lat": 52.1, "lon": 5.3},
        ]
        for c in countries:
            session.run(
                """
                MERGE (n:Country { id: $id })
                SET n.name = $name, n.code = $code, n.lat = $lat, n.lon = $lon
                """,
                c,
            )

        # ----- Ports -----
        ports = [
            {"id": "port_la", "name": "Port of Los Angeles", "code": "USLAX", "lat": 33.75, "lon": -118.27},
            {"id": "port_shanghai", "name": "Port of Shanghai", "code": "CNSHA", "lat": 31.23, "lon": 121.47},
            {"id": "port_hamburg", "name": "Port of Hamburg", "code": "DEHAM", "lat": 53.54, "lon": 9.93},
            {"id": "port_rotterdam", "name": "Port of Rotterdam", "code": "NLRTM", "lat": 51.92, "lon": 4.48},
            {"id": "port_vungtau", "name": "Vung Tau Port", "code": "VNVUT", "lat": 10.35, "lon": 107.08},
        ]
        port_country = [("port_la", "usa"), ("port_shanghai", "chn"), ("port_hamburg", "deu"), ("port_rotterdam", "nld"), ("port_vungtau", "vnm")]
        for p in ports:
            session.run(
                """
                MERGE (n:Port { id: $id })
                SET n.name = $name, n.code = $code, n.lat = $lat, n.lon = $lon
                """,
                p,
            )
        for port_id, country_id in port_country:
            session.run(
                "MATCH (p:Port { id: $port_id }), (c:Country { id: $country_id }) MERGE (p)-[:LOCATED_IN]->(c)",
                port_id=port_id, country_id=country_id,
            )

        # ----- Companies -----
        companies = [
            {"id": "acme", "name": "Acme Corp", "lat": 37.39, "lon": -122.08},
            {"id": "global_motors", "name": "Global Motors", "lat": 48.14, "lon": 11.58},
            {"id": "techflow", "name": "TechFlow Inc", "lat": 40.71, "lon": -74.01},
        ]
        company_country = [("acme", "usa"), ("global_motors", "deu"), ("techflow", "usa")]
        for c in companies:
            session.run(
                """
                MERGE (n:Company { id: $id })
                SET n.name = $name, n.lat = $lat, n.lon = $lon
                """,
                c,
            )
        for company_id, country_id in company_country:
            session.run(
                "MATCH (c:Company { id: $company_id }), (co:Country { id: $country_id }) MERGE (c)-[:LOCATED_IN]->(co)",
                company_id=company_id, country_id=country_id,
            )

        # ----- Suppliers (Tier 1–4) -----
        suppliers = [
            # Tier 1 (direct to companies)
            {"id": "sup_t1_alpha", "name": "Alpha Components Inc", "tier": 1, "lat": 33.64, "lon": -117.74},
            {"id": "sup_t1_beta", "name": "Beta Logistics GmbH", "tier": 1, "lat": 50.11, "lon": 8.68},
            {"id": "sup_t1_gamma", "name": "Gamma Materials Co", "tier": 1, "lat": 22.28, "lon": 114.16},
            {"id": "sup_t1_delta", "name": "Delta Systems LLC", "tier": 1, "lat": 29.76, "lon": -95.37},
            # Tier 2
            {"id": "sup_t2_east", "name": "Eastern Foundry Ltd", "tier": 2, "lat": 31.23, "lon": 121.47},
            {"id": "sup_t2_west", "name": "Western Alloys", "tier": 2, "lat": 33.75, "lon": -118.27},
            {"id": "sup_t2_north", "name": "Northern Circuits", "tier": 2, "lat": 35.68, "lon": 139.69},
            {"id": "sup_t2_south", "name": "Southern Petrochem", "tier": 2, "lat": 10.82, "lon": 106.73},
            # Tier 3
            {"id": "sup_t3_mining_a", "name": "Rare Earth Mining Co", "tier": 3, "lat": 30.59, "lon": 114.31},
            {"id": "sup_t3_mining_b", "name": "Pacific Ore Corp", "tier": 3, "lat": -33.87, "lon": 151.21},
            {"id": "sup_t3_chem", "name": "ChemBase Industries", "tier": 3, "lat": 51.92, "lon": 4.48},
            # Tier 4
            {"id": "sup_t4_raw_a", "name": "Raw Materials Global", "tier": 4, "lat": -23.55, "lon": -46.63},
            {"id": "sup_t4_raw_b", "name": "Elemental Sources", "tier": 4, "lat": -26.20, "lon": 28.04},
        ]
        for s in suppliers:
            session.run(
                """
                MERGE (n:Supplier { id: $id })
                SET n.name = $name, n.tier = $tier, n.lat = $lat, n.lon = $lon
                """,
                s,
            )
        # Supplier -> Country
        sup_country = [
            ("sup_t1_alpha", "usa"), ("sup_t1_beta", "deu"), ("sup_t1_gamma", "chn"), ("sup_t1_delta", "usa"),
            ("sup_t2_east", "chn"), ("sup_t2_west", "usa"), ("sup_t2_north", "jpn"), ("sup_t2_south", "vnm"),
            ("sup_t3_mining_a", "chn"), ("sup_t3_mining_b", "usa"), ("sup_t3_chem", "nld"),
            ("sup_t4_raw_a", "usa"), ("sup_t4_raw_b", "usa"),
        ]
        for sup_id, country_id in sup_country:
            session.run(
                "MATCH (s:Supplier { id: $sup_id }), (c:Country { id: $country_id }) MERGE (s)-[:LOCATED_IN]->(c)",
                sup_id=sup_id, country_id=country_id,
            )

        # ----- Factories -----
        factories = [
            {"id": "fac_shenzhen", "name": "Shenzhen Assembly Plant", "lat": 22.54, "lon": 114.06},
            {"id": "fac_detroit", "name": "Detroit Manufacturing", "lat": 42.33, "lon": -83.05},
            {"id": "fac_vietnam", "name": "Vietnam Electronics Hub", "lat": 10.82, "lon": 106.73},
        ]
        fac_country = [("fac_shenzhen", "chn"), ("fac_detroit", "usa"), ("fac_vietnam", "vnm")]
        for f in factories:
            session.run(
                """
                MERGE (n:Factory { id: $id })
                SET n.name = $name, n.lat = $lat, n.lon = $lon
                """,
                f,
            )
        for fac_id, country_id in fac_country:
            session.run(
                "MATCH (f:Factory { id: $fac_id }), (c:Country { id: $country_id }) MERGE (f)-[:LOCATED_IN]->(c)",
                fac_id=fac_id, country_id=country_id,
            )

        # ----- SUPPLIES_TO: Supplier -> Company, Supplier -> Supplier (tier chain) -----
        supplies_to = [
            ("sup_t1_alpha", "acme"), ("sup_t1_beta", "global_motors"), ("sup_t1_gamma", "acme"), ("sup_t1_gamma", "techflow"),
            ("sup_t1_delta", "techflow"),
            ("sup_t2_east", "sup_t1_gamma"), ("sup_t2_west", "sup_t1_alpha"), ("sup_t2_north", "sup_t1_beta"), ("sup_t2_south", "sup_t1_gamma"),
            ("sup_t3_mining_a", "sup_t2_east"), ("sup_t3_mining_b", "sup_t2_west"), ("sup_t3_chem", "sup_t2_north"), ("sup_t3_chem", "sup_t2_south"),
            ("sup_t4_raw_a", "sup_t3_mining_a"), ("sup_t4_raw_b", "sup_t3_mining_b"),
        ]
        for from_id, to_id in supplies_to:
            session.run(
                """
                MATCH (a) WHERE a.id = $from_id AND (a:Supplier OR a:Company)
                MATCH (b) WHERE b.id = $to_id AND (b:Supplier OR b:Company)
                MERGE (a)-[:SUPPLIES_TO { product: 'general' }]->(b)
                """,
                from_id=from_id, to_id=to_id,
            )

        # ----- DEPENDS_ON: Company -> Supplier, Supplier -> Supplier -----
        depends_on = [
            ("acme", "sup_t1_alpha"), ("acme", "sup_t1_gamma"), ("global_motors", "sup_t1_beta"), ("techflow", "sup_t1_gamma"), ("techflow", "sup_t1_delta"),
            ("sup_t1_gamma", "sup_t2_east"), ("sup_t1_gamma", "sup_t2_south"), ("sup_t1_alpha", "sup_t2_west"), ("sup_t1_beta", "sup_t2_north"),
            ("sup_t2_east", "sup_t3_mining_a"), ("sup_t2_west", "sup_t3_mining_b"), ("sup_t2_north", "sup_t3_chem"), ("sup_t2_south", "sup_t3_chem"),
            ("sup_t3_mining_a", "sup_t4_raw_a"), ("sup_t3_mining_b", "sup_t4_raw_b"),
        ]
        for from_id, to_id in depends_on:
            session.run(
                """
                MATCH (a) WHERE a.id = $from_id AND (a:Company OR a:Supplier)
                MATCH (b) WHERE b.id = $to_id AND b:Supplier
                MERGE (a)-[:DEPENDS_ON]->(b)
                """,
                from_id=from_id, to_id=to_id,
            )

        # ----- SHIPS_VIA: Supplier/Factory -> Port -----
        ships_via = [
            ("sup_t1_gamma", "port_shanghai"), ("sup_t2_east", "port_shanghai"), ("sup_t2_south", "port_vungtau"),
            ("sup_t1_alpha", "port_la"), ("sup_t2_west", "port_la"), ("sup_t1_beta", "port_hamburg"), ("sup_t2_north", "port_hamburg"),
            ("sup_t3_chem", "port_rotterdam"), ("fac_shenzhen", "port_shanghai"), ("fac_detroit", "port_la"), ("fac_vietnam", "port_vungtau"),
        ]
        for from_id, port_id in ships_via:
            session.run(
                """
                MATCH (a) WHERE a.id = $from_id AND (a:Supplier OR a:Factory)
                MATCH (p:Port { id: $port_id })
                MERGE (a)-[:SHIPS_VIA]->(p)
                """,
                from_id=from_id, port_id=port_id,
            )


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        driver.verify_connectivity()
    except Exception as e:
        print("Neo4j connection failed. Is the DB running? (e.g. docker compose up -d)", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)
    try:
        print("Applying schema...")
        run_schema(driver)
        print("Clearing existing graph...")
        clear_graph(driver)
        print("Seeding mock data...")
        seed(driver)
        print("Done.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
