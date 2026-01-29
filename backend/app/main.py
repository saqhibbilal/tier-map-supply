from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_driver, get_driver
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_driver().verify_connectivity()
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
    return {"status": "ok"}
