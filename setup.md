# Supply Chain Risk — Setup

Step-by-step setup for running the app locally after cloning the repo.

---

## Prerequisites

- **Docker** (for Neo4j)
- **Python 3.10+** (for backend and seed script)
- **Node.js 18+** and **npm** (for frontend)

---

## 1. Clone and go to project root

```bash
git clone <repo-url>
cd supplymap
```

All commands below assume you are in the **project root** (`supplymap/`) unless stated otherwise.

---

## 2. Environment

Copy the example env file and adjust if needed:

```bash
copy .env.example .env
```

(On macOS/Linux: `cp .env.example .env`)

Default values work for local runs:

| Variable       | Default               | Used by              |
| -------------- | --------------------- | -------------------- |
| NEO4J_URI      | bolt://localhost:7687 | Backend, seed script |
| NEO4J_USER     | neo4j                 | Backend, seed script |
| NEO4J_PASSWORD | supplymap-dev         | Backend, seed script |

---

## 3. Start Neo4j (Docker)

**Where:** Project root (where `docker-compose.yml` is).

```bash
docker compose up -d
```

- **Browser UI:** http://localhost:7474
- **Bolt (driver):** `bolt://localhost:7687`
- **Login:** `neo4j` / `supplymap-dev` (or whatever you set in `.env` as `NEO4J_PASSWORD`).

**Wait 30–60 seconds** after the container starts. Neo4j needs time before it accepts connections on port 7687.

Check that the container is running:

```bash
docker ps
```

You should see `supplymap-neo4j` with status **Up**. If you see nothing, the container may have exited (see **Troubleshooting — Docker** below).

---

## 4. Seed the graph

**Where:** Project root.

One-time setup for the Python seed script:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r data/requirements.txt
```

(On macOS/Linux: `.venv/bin/activate`)

Run the seed script (creates schema and loads mock data):

```bash
python data/seed_mock_data.py
```

You should see: `Applying schema...`, `Clearing existing graph...`, `Seeding mock data...`, `Done.`

- If you get **connection refused** or **incomplete handshake**: Neo4j is not ready yet. Wait a minute and run the script again.
- If you **recreate the Neo4j volume** (e.g. `docker compose down -v`), run this seed script again after starting Neo4j.

---

## 5. Start the backend

**Where:** Project root, then `backend/`.

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

(On macOS/Linux: `venv/bin/activate`)

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health — if Neo4j is up, response includes `"neo4j": "connected"`.

Leave this terminal running. The backend reads `.env` from the **project root** (one level up from `backend/`).

---

## 6. Start the frontend

**Where:** New terminal, project root, then `frontend/`.

```bash
cd supplymap/frontend
npm install
npm run dev
```

- **App:** http://localhost:5173

The frontend proxies `/api` to `http://localhost:8000`, so the backend must be running.

---

## Order of operations (quick reference)

1. **Project root:** `copy .env.example .env`
2. **Project root:** `docker compose up -d` → wait 30–60 s
3. **Project root:** `python -m venv .venv` → activate → `pip install -r data/requirements.txt` → `python data/seed_mock_data.py`
4. **backend/:** venv → `pip install -r requirements.txt` → `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
5. **frontend/:** `npm install` → `npm run dev` → open http://localhost:5173

---

## Troubleshooting

### Docker — Neo4j container exits or won’t start

- **Invalid `NEO4J_AUTH`:** Neo4j expects `username/password`. In `docker-compose.yml` it must be `neo4j/${NEO4J_PASSWORD:-supplymap-dev}` (no space). If you see “supplymap-dev is invalid”, the format was wrong; the repo version is already correct.
- **Container starts then stops:** We use `restart: unless-stopped` and lower heap (512m) so the container restarts if it exits and is less likely to be killed by memory. If it still stops, run `docker compose down -v` and then `docker compose up -d` again (this removes the DB volume; you must **re-run the seed script** after Neo4j is up).
- **No containers listed:** Run `docker compose up -d` from the **project root** (where `docker-compose.yml` is).

### Neo4j — Connection refused / incomplete handshake

- The database is not ready yet. Wait **30–60 seconds** after `docker compose up -d`, then retry the seed script or the backend.
- Check logs: `docker compose logs neo4j`. Wait until you see “Bolt enabled” or “Started.”

### Backend — Application startup failed (Neo4j)

- The app still starts; it only logs a warning if Neo4j is down. Start Neo4j first, then (re)start the backend. Call http://localhost:8000/health to confirm `neo4j: "connected"`.

### Frontend — Proxy error / ECONNREFUSED to :8000

- The backend is not running or not on port 8000. Start the backend (step 5) and keep it running.

### API — 500 on supply-chain or impact

- Usually a Cypher/Neo4j issue. Ensure the **seed script** has been run at least once so the graph and schema exist. Check backend logs for the exact error.

---

## Repo layout (for reference)

```
supplymap/
├── .env.example          # Copy to .env
├── docker-compose.yml    # Neo4j
├── data/
│   ├── requirements.txt  # deps for seed script
│   ├── schema.cypher     # Neo4j constraints/indexes
│   └── seed_mock_data.py # Run this to seed the graph
├── backend/
│   ├── requirements.txt
│   └── app/              # FastAPI app
├── frontend/
│   ├── package.json
│   └── src/              # React + Leaflet app
└── docs/
    └── schema.md         # Graph schema description
```
