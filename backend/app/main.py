import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_driver, get_driver
from app.routes import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_driver().verify_connectivity()
        logger.info("Neo4j connected")
    except Exception as e:
        logger.warning("Neo4j not available at startup: %s. Start Neo4j (docker compose up -d) and retry API calls.", e)
    yield
    close_driver()


app = FastAPI(
    title="Supply Chain API",
    description="Supply chain dependency and risk visualization API",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health")
def health():
    try:
        get_driver().verify_connectivity()
        return {"status": "ok", "neo4j": "connected"}
    except Exception as e:
        return {"status": "ok", "neo4j": "disconnected", "detail": str(e)}
