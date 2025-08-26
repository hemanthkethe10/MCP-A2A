# Placeholder for A2A agent task logic 

import os
import logging
import uuid
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
import httpx
from external_agents import github_agent, summarizer, emailer

logger = logging.getLogger("a2a_agent.tasks")

router = APIRouter()

# In-memory task store for async mode
task_store: Dict[str, Dict[str, Any]] = {}

# MCP server base URL
MCP_BASE = os.environ.get("MCP_BASE", "http://localhost:8001")

# Check async mode from env
ASYNC_MODE = os.environ.get("A2A_ASYNC_MODE", "false").lower() == "true"

@router.post("/tasks/submit")
async def submit_task(request: Request):
    """Accept a task request. If async mode, return task_id and process in background. Else, process synchronously."""
    data = await request.json()
    logger.info(f"Received task submission: {data}")
    if ASYNC_MODE:
        task_id = str(uuid.uuid4())
        task_store[task_id] = {"status": "submitted", "result": None, "input": data}
        asyncio.create_task(process_task_async(task_id, data))
        logger.info(f"Task {task_id} submitted for async processing.")
        return {"task_id": task_id, "status": "submitted"}
    else:
        logger.info("Processing task synchronously.")
        result = await process_task(data)
        return {"status": "completed", "result": result}

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get the status/result of an async task."""
    if task_id not in task_store:
        logger.warning(f"Task {task_id} not found.")
        raise HTTPException(status_code=404, detail="Task not found")
    return task_store[task_id]

async def process_task_async(task_id: str, data: dict):
    logger.info(f"Async processing for task {task_id} started.")
    task_store[task_id]["status"] = "working"
    try:
        result = await process_task(data)
        task_store[task_id]["result"] = result
        task_store[task_id]["status"] = "completed"
        logger.info(f"Task {task_id} completed.")
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task_store[task_id]["result"] = str(e)
        task_store[task_id]["status"] = "failed"

def parse_task(data: dict):
    """Parse the task input and determine what actions to take."""
    # Example: {"action": "file_search", "directory": "/tmp", "pattern": ".pdf"}
    # Or: {"action": "weather_alerts", "state": "CA"}
    # Or: {"action": "weather_forecast", "lat": 37.77, "lon": -122.41}
    return data.get("action"), data

async def process_task(data: dict):
    action, params = parse_task(data)
    logger.info(f"Processing action: {action} with params: {params}")
    async with httpx.AsyncClient() as client:
        if action == "file_search":
            resp = await client.get(f"{MCP_BASE}/files/search", params={"directory": params["directory"], "pattern": params.get("pattern", "")})
            resp.raise_for_status()
            return resp.json()
        elif action == "weather_alerts":
            resp = await client.get(f"{MCP_BASE}/weather/alerts", params={"state": params["state"]})
            resp.raise_for_status()
            return resp.text
        elif action == "weather_forecast":
            resp = await client.get(f"{MCP_BASE}/weather/forecast", params={"lat": params["lat"], "lon": params["lon"]})
            resp.raise_for_status()
            return resp.json()
        elif action == "combo":
            # Example: combo action: search files, then get weather for each file's date/location (simplified)
            files_resp = await client.get(f"{MCP_BASE}/files/search", params={"directory": params["directory"], "pattern": params.get("pattern", "")})
            files_resp.raise_for_status()
            files = files_resp.json()
            # For demo, just get weather for the first file if lat/lon provided
            if files and "lat" in params and "lon" in params:
                weather_resp = await client.get(f"{MCP_BASE}/weather/forecast", params={"lat": params["lat"], "lon": params["lon"]})
                weather_resp.raise_for_status()
                weather = weather_resp.json()
                return {"files": files, "weather": weather}
            return {"files": files}
        elif action == "github_issues":
            # params: {"action": "github_issues", "repo": "owner/repo", "state": "open"}
            logger.info(f"Fetching GitHub issues for repo: {params.get('repo')}")
            issues = github_agent.fetch_issues(params["repo"], params.get("state", "open"))
            return issues
        elif action == "github_prs":
            # params: {"action": "github_prs", "repo": "owner/repo", "state": "open"}
            logger.info(f"Fetching GitHub PRs for repo: {params.get('repo')}")
            prs = github_agent.fetch_pull_requests(params["repo"], params.get("state", "open"))
            return prs
        elif action == "summarize_and_email_pdfs":
            # params: {"action": "summarize_and_email_pdfs", "directory": "/path", "recipient": "user@example.com"}
            directory = params["directory"]
            recipient = params["email"]
            logger.info(f"Searching for PDF files in {directory}")
            files_resp = await client.get(f"{MCP_BASE}/files/search", params={"directory": directory, "pattern": ".pdf"})
            files_resp.raise_for_status()
            pdf_files = files_resp.json()
            if not pdf_files:
                logger.warning("No PDF files found.")
                return {"status": "no_pdfs_found", "files": [], "summaries": [], "email_sent": False}
            summaries = []
            for pdf in pdf_files:
                logger.info(f"Summarizing PDF: {pdf}")
                summary = summarizer.summarize_pdf(pdf)
                summaries.append({"file": pdf, "summary": summary})
            email_body = "PDF Summaries:\n\n" + "\n\n".join(f"{os.path.basename(s['file'])}:\n{s['summary']}" for s in summaries)
            subject = f"PDF Summaries for {directory}"
            email_sent = emailer.send_email(recipient, subject, email_body)
            logger.info(f"Email sent: {email_sent}")
            return {"status": "completed", "files": pdf_files, "summaries": summaries, "email_sent": email_sent}
        else:
            logger.warning(f"Unknown action: {action}")
            return {"error": f"Unknown action: {action}"} 