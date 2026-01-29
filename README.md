# Supply Chain Dependency & Risk Visualization

Multi-tier supply chain dependency and risk visualization using Neo4j, with a React + Leaflet frontend and FastAPI backend.

---

## Phase 1: Neo4j and data

### Start Neo4j (Docker)

From the project root:

```bash
docker compose up -d
```

- **Browser UI:** http://localhost:7474
- **Bolt (driver):** `bolt://localhost:7687`

Default auth is set via `NEO4J_AUTH` in `docker-compose.yml`. To use a custom password, copy `.env.example` to `.env` and set `NEO4J_PASSWORD`; the compose file reads it.

### Environment

Copy `.env.example` to `.env` and adjust if needed. Used by seed scripts and (later) the backend.

| Variable         | Default                 | Description    |
| ---------------- | ----------------------- | -------------- |
| `NEO4J_URI`      | `bolt://localhost:7687` | Neo4j Bolt URI |
| `NEO4J_USER`     | `neo4j`                 | Neo4j user     |
| `NEO4J_PASSWORD` | `supplymap-dev`         | Neo4j password |

### Phase 1 — Schema

- **Constraints and indexes:** `data/schema.cypher` (run once after Neo4j is up).
- **Schema docs and example queries:** [docs/schema.md](docs/schema.md).

### Phase 1 — Seed mock data

From the project root, with Neo4j running:

```bash
# Optional: create a venv and install deps for the seed script
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r data/requirements.txt

# Run the seed script (applies schema, clears graph, loads mock data)
python data/seed_mock_data.py
```

The script creates: 3 companies, Tier-1–4 suppliers, factories, ports, and countries, with `SUPPLIES_TO`, `DEPENDS_ON`, `SHIPS_VIA`, and `LOCATED_IN` relationships so variable-depth traversals return plausible paths.
