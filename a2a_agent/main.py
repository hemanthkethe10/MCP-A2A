import logging
from fastapi import FastAPI
from .tasks import router
import os
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("a2a_agent")

app = FastAPI(title="A2A Agent Example")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:8001"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    logger.info("A2A Agent is starting up...")

# Mount the tasks router
logger.info("Mounting tasks router.")
app.include_router(router)

# Serve agent_card.json for discovery
@app.get("/.well-known/agent.json")
def agent_card():
    logger.info("Serving agent_card.json for discovery.")
    return FileResponse(os.path.join(os.path.dirname(__file__), "agent_card.json"), media_type="application/json")

# Import tasks to register endpoints
from . import tasks  # noqa 