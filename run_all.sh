#!/bin/bash

# Run MCP server
echo "Starting MCP server..."
uvicorn mcp_server.main:app --reload --port 8001 &
MCP_PID=$!

# Run A2A agent
echo "Starting A2A agent..."
uvicorn a2a_agent.main:app --reload --port 8002 &
A2A_PID=$!

# Wait for both processes
wait $MCP_PID $A2A_PID 