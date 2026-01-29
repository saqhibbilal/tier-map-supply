from fastapi import APIRouter

from app.routes import companies, suppliers, ports, supply_chain, impact

api_router = APIRouter(prefix="/api")
api_router.include_router(companies.router, prefix="/companies")
api_router.include_router(suppliers.router, prefix="/suppliers")
api_router.include_router(ports.router, prefix="/ports")
api_router.include_router(supply_chain.router, prefix="/supply-chain")
api_router.include_router(impact.router, prefix="/impact")
