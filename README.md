# Supply Chain Risk

This project is a multi-tier supply chain dependency and risk visualization system built on **Neo4j**. It models Tier-1 through Tier-4 supplier relationships as a graph: companies, suppliers, factories, ports, and countries are nodes; relationships such as SUPPLIES_TO, DEPENDS_ON, SHIPS_VIA, and LOCATED_IN capture material flow and operational dependencies across geographies. Users select a focal company, upstream depth, and optional disruption scenario (supplier failure or port closure). The backend runs **Cypher** traversals—variable-depth path queries (e.g. `MATCH path = (c:Company)<-[:SUPPLIES_TO*1..n]-(upstream)` for upstream mapping, and impact queries for downstream exposure)—and returns geospatially enriched nodes and edges. The frontend renders these on an interactive world map with tier-coded markers and connection lines, giving a clear **overview and insight** into network structure, single points of failure, and **risk propagation**. The tool supports **risk management** and strategic planning by exposing supplier dependency, multi-echelon visibility, and what-if impact (e.g. port or supplier disruption). Business value includes improved **supply chain visibility**, **resilience assessment**, and **contingency planning**. We plan to optimize with richer tooltips, progressive disclosure, export options, and path highlighting; a **chatbot integration** is planned for conversational queries (e.g. “Show Tier-2 suppliers for Acme” or “Impact if Rotterdam closes”). The stack is Neo4j, FastAPI, and React with Leaflet.

---

## Screenshots

**Supply chain map (focal company, upstream tiers)**

![Supply chain map](Screenshot%202026-01-30%20175327.jpg)

**Impact view: supplier failure (which supplier, downstream impact)**

![Supplier failure impact](Screenshot%202026-01-30%20175431.jpg)

**Impact view: port closure (which port, affected nodes and connections)**

![Port closure impact](Screenshot%202026-01-30%20175636.jpg)

---
