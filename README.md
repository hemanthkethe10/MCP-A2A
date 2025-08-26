# MCP-A2A Sample Project

This project demonstrates how to build a real-world MCP (Model Context Protocol) server and an A2A (Agent2Agent) agent using Python and FastAPI. It includes integration with an external open-source agent (GitHub) and provides clear examples, code, and documentation for both protocols.

## Project Structure

```
MCP-A2A/
  ├── mcp_server/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── handlers.py
  │   └── resources.py
  ├── a2a_agent/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── agent_card.json
  │   └── tasks.py
  ├── external_agents/
  │   └── github_agent.py
  ├── tests/
  │   └── test_integration.py
  ├── README.md
  ├── requirements.txt
  └── run_all.sh
```

## Components

- **mcp_server/**: Implements an MCP server exposing real-world tools (file search, weather info).
- **a2a_agent/**: Implements an A2A-compliant agent that can receive tasks, interact with the MCP server, and manage task lifecycles.
- **external_agents/**: Example integration with an open-source agent (GitHub API).
- **tests/**: Integration tests for the workflow.
- **requirements.txt**: Python dependencies.
- **run_all.sh**: Script to run all services for demo/testing.

## Protocols

- **MCP (Model Context Protocol):** Standardizes how AI applications connect to data sources and tools. [Learn more](https://modelcontextprotocol.io/introduction)
- **A2A (Agent2Agent):** Defines how agents communicate, delegate, and collaborate on tasks. [Learn more](https://google-a2a.github.io/A2A/topics/key-concepts/)

## How to Use

1. Install dependencies: `pip install -r requirements.txt`
2. Start the MCP server: `python mcp_server/main.py`
3. Start the A2A agent: `python a2a_agent/main.py`
4. Run integration tests: `python tests/test_integration.py`

---

This project is intended for educational and experimental purposes. See inline documentation for details on each protocol and component. 