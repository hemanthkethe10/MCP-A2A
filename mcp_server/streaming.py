"""
WebSocket streaming handlers for real-time communication with LangGraph agents
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from datetime import datetime

# LangGraph imports
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain.tools import BaseTool
from langchain.callbacks.base import BaseCallbackHandler

# Import our advanced LangGraph agent
from .langgraph_agent import create_advanced_agent, initialize_agent_state

logger = logging.getLogger("mcp_server.streaming")

router = APIRouter()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_sessions: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_sessions[session_id] = {
            "created_at": datetime.now(),
            "messages": [],
            "status": "connected"
        }
        logger.info(f"WebSocket connection established for session {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.connection_sessions:
            self.connection_sessions[session_id]["status"] = "disconnected"
        logger.info(f"WebSocket connection closed for session {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                return False
        return False

    async def broadcast(self, message: dict):
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")

manager = ConnectionManager()

# Pydantic models for API documentation
class StreamMessage(BaseModel):
    type: str
    content: str
    session_id: str
    timestamp: Optional[str] = None

class StreamResponse(BaseModel):
    type: str
    content: str
    session_id: str
    agent_type: Optional[str] = None
    step_info: Optional[Dict[str, Any]] = None

class SessionInfo(BaseModel):
    session_id: str
    status: str
    created_at: str
    message_count: int

# Custom callback handler for streaming LangGraph agent responses
class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, session_id: str, manager: ConnectionManager):
        self.session_id = session_id
        self.manager = manager

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        await self.manager.send_personal_message({
            "type": "agent_thinking",
            "content": "Agent is processing your request...",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }, self.session_id)

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.manager.send_personal_message({
            "type": "token_stream",
            "content": token,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }, self.session_id)

    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        await self.manager.send_personal_message({
            "type": "tool_start",
            "content": f"Using tool: {serialized.get('name', 'Unknown')}",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }, self.session_id)

    async def on_tool_end(self, output: str, **kwargs):
        await self.manager.send_personal_message({
            "type": "tool_result",
            "content": f"Tool completed with output: {output[:200]}...",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }, self.session_id)

# Mock LangGraph tools for demonstration (simplified for compatibility)
def mock_file_search(directory: str, pattern: str = "") -> str:
    """Search for files in a directory"""
    import os
    if not os.path.isdir(directory):
        return f"Directory not found: {directory}"
    
    files = []
    for root, _, file_list in os.walk(directory):
        for f in file_list:
            if pattern in f:
                files.append(os.path.join(root, f))
    
    return f"Found {len(files)} files matching pattern '{pattern}' in {directory}"

def mock_data_analysis(data_type: str, analysis_type: str = "summary") -> str:
    """Analyze data and provide insights"""
    # Mock analysis
    if analysis_type == "summary":
        return f"Summary analysis of {data_type}: Data contains patterns indicating normal distribution with moderate variance."
    elif analysis_type == "trends":
        return f"Trend analysis of {data_type}: Upward trend observed over the last quarter with seasonal variations."
    else:
        return f"Analysis type '{analysis_type}' completed for {data_type}."

# LangGraph Agent State
class AgentState(BaseModel):
    messages: List[BaseMessage] = []
    current_task: Optional[str] = None
    tools_used: List[str] = []
    session_id: str
    step_count: int = 0

# Agent workflow functions
async def analyze_input(state: AgentState, session_id: str) -> AgentState:
    """Analyze user input and determine next steps"""
    logger.info(f"Analyzing input for session {session_id}")
    
    last_message = state.messages[-1] if state.messages else None
    if not last_message:
        return state
    
    user_input = last_message.content.lower()
    
    # Simple task classification
    if "file" in user_input or "search" in user_input:
        state.current_task = "file_search"
    elif "analyze" in user_input or "data" in user_input:
        state.current_task = "data_analysis"
    else:
        state.current_task = "general_chat"
    
    state.step_count += 1
    
    # Send update to client
    await manager.send_personal_message({
        "type": "agent_step",
        "content": f"Identified task: {state.current_task}",
        "session_id": session_id,
        "step_info": {"step": state.step_count, "task": state.current_task},
        "timestamp": datetime.now().isoformat()
    }, session_id)
    
    return state

async def execute_task(state: AgentState, session_id: str) -> AgentState:
    """Execute the identified task"""
    logger.info(f"Executing task {state.current_task} for session {session_id}")
    
    response_content = ""
    
    if state.current_task == "file_search":
        result = mock_file_search("/tmp", "*.txt")  # Mock parameters
        response_content = f"File search completed: {result}"
        state.tools_used.append("file_search")
        
    elif state.current_task == "data_analysis":
        result = mock_data_analysis("sample_data", "summary")
        response_content = f"Data analysis completed: {result}"
        state.tools_used.append("data_analysis")
        
    else:
        response_content = "I'm a helpful assistant. I can help you search files or analyze data. What would you like me to do?"
    
    # Add AI response to messages
    state.messages.append(AIMessage(content=response_content))
    state.step_count += 1
    
    # Send streaming response
    await manager.send_personal_message({
        "type": "agent_response",
        "content": response_content,
        "session_id": session_id,
        "step_info": {"step": state.step_count, "tools_used": state.tools_used},
        "timestamp": datetime.now().isoformat()
    }, session_id)
    
    return state

def should_continue(state: AgentState) -> str:
    """Determine if the agent should continue processing"""
    return "end"

# Create LangGraph workflow
def create_agent_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyze", analyze_input)
    workflow.add_node("execute", execute_task)
    
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "execute")
    workflow.add_conditional_edges("execute", should_continue, {"end": END})
    
    return workflow.compile()

# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    agent_workflow = create_advanced_agent()
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection_established",
            "content": "Connected to LangGraph streaming agent. Send me a message!",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }, session_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            logger.info(f"Received message from {session_id}: {message_data}")
            
            # Store message in session
            manager.connection_sessions[session_id]["messages"].append(message_data)
            
            user_content = message_data.get("content", "")
            
            # Initialize agent state with the advanced LangGraph agent
            agent_state = initialize_agent_state(session_id, user_content)
            
            # Process with advanced LangGraph agent
            try:
                # Send processing started message
                await manager.send_personal_message({
                    "type": "agent_processing_start",
                    "content": "🤖 Advanced LangGraph agent is processing your request...",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }, session_id)
                
                # Execute workflow with streaming
                step_count = 0
                async for step_output in agent_workflow.astream(agent_state):
                    step_count += 1
                    logger.info(f"Agent step {step_count} output: {step_output}")
                    
                    # Extract step information
                    current_node = list(step_output.keys())[0] if step_output else 'unknown'
                    node_state = step_output.get(current_node, {}) if step_output else {}
                    
                    # Send detailed step updates
                    await manager.send_personal_message({
                        "type": "agent_step_detailed",
                        "content": f"📋 Step {step_count}: {current_node.replace('_', ' ').title()}",
                        "session_id": session_id,
                        "step_info": {
                            "step_number": step_count,
                            "node_name": current_node,
                            "current_step": node_state.get("current_step", "unknown"),
                            "tools_used": node_state.get("tools_used", []),
                            "confidence_score": node_state.get("confidence_score", 0.0)
                        },
                        "timestamp": datetime.now().isoformat()
                    }, session_id)
                    
                    # If this step generated a response message, send it
                    if "messages" in node_state:
                        messages = node_state["messages"]
                        if messages and isinstance(messages[-1], AIMessage):
                            await manager.send_personal_message({
                                "type": "agent_response",
                                "content": messages[-1].content,
                                "session_id": session_id,
                                "agent_type": "langgraph_advanced",
                                "step_info": {
                                    "step_number": step_count,
                                    "confidence_score": node_state.get("confidence_score", 0.0),
                                    "tools_used": node_state.get("tools_used", [])
                                },
                                "timestamp": datetime.now().isoformat()
                            }, session_id)
                    
                    # Add delay for better user experience
                    await asyncio.sleep(0.3)
                
                # Send completion message
                await manager.send_personal_message({
                    "type": "agent_processing_complete",
                    "content": "✅ Processing completed! Feel free to ask another question.",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }, session_id)
                
            except Exception as e:
                logger.error(f"Error in advanced agent workflow: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "content": f"❌ Agent error: {str(e)}",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }, session_id)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"Client {session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)

# REST endpoints for session management
@router.get("/streaming/sessions", response_model=List[SessionInfo])
async def get_active_sessions():
    """Get list of active streaming sessions"""
    sessions = []
    for session_id, session_data in manager.connection_sessions.items():
        sessions.append(SessionInfo(
            session_id=session_id,
            status=session_data["status"],
            created_at=session_data["created_at"].isoformat(),
            message_count=len(session_data["messages"])
        ))
    return sessions

@router.get("/streaming/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    if session_id not in manager.connection_sessions:
        return JSONResponse(status_code=404, content={"detail": "Session not found"})
    
    session_data = manager.connection_sessions[session_id]
    return SessionInfo(
        session_id=session_id,
        status=session_data["status"],
        created_at=session_data["created_at"].isoformat(),
        message_count=len(session_data["messages"])
    )

@router.post("/streaming/broadcast")
async def broadcast_message(message: StreamMessage):
    """Broadcast a message to all active connections"""
    await manager.broadcast({
        "type": "broadcast",
        "content": message.content,
        "sender": "system",
        "timestamp": datetime.now().isoformat()
    })
    return {"status": "broadcast_sent", "message": message.content}

@router.delete("/streaming/sessions/{session_id}")
async def close_session(session_id: str):
    """Close a specific session"""
    if session_id in manager.active_connections:
        await manager.active_connections[session_id].close()
        manager.disconnect(session_id)
        return {"status": "session_closed", "session_id": session_id}
    else:
        return JSONResponse(status_code=404, content={"detail": "Session not found"})
