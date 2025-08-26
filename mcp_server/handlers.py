import logging
from fastapi import APIRouter
from . import resources

logger = logging.getLogger("mcp_server.handlers")

router = APIRouter()

@router.get("/health")
def health_check():
    logger.info("Health check called.")
    return {"status": "ok"}

# Register resources endpoints
logger.info("Registering resources router.")
router.include_router(resources.router) 