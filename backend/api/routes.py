from fastapi import APIRouter

from api.agent_routes import router as agent_router
from api.integration_routes import router as integration_router
from api.activity_routes import router as activity_router
from api.approval_routes import router as approval_router
from api.health_routes import router as health_router

router = APIRouter()

router.include_router(agent_router, prefix="/agent", tags=["Agent"])
router.include_router(integration_router, prefix="/integrations", tags=["Integrations"])
router.include_router(activity_router, prefix="/activity", tags=["Activity"])
router.include_router(approval_router, prefix="/approvals", tags=["Approvals"])
router.include_router(health_router, prefix="/health", tags=["Health"])
