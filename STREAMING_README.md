# 🚀 WebSocket Streaming with LangGraph Agents

This document describes the new streaming functionality added to the MCP-A2A project, featuring real-time WebSocket communication with advanced LangGraph-based AI agents.

## 🌟 Features

### WebSocket Streaming
- **Real-time Communication**: Bidirectional WebSocket connections for instant message exchange
- **Session Management**: Unique session IDs for tracking individual conversations
- **Connection Monitoring**: Real-time status updates and connection health monitoring
- **Broadcast Capabilities**: Send messages to all connected clients

### LangGraph Agent System
- **Advanced Workflow Engine**: Multi-step agent processing with clear state transitions
- **Tool Integration**: Built-in tools for text analysis, knowledge search, metrics calculation, and workflow processing
- **Streaming Responses**: Step-by-step updates during agent processing
- **Confidence Scoring**: AI confidence levels for each response
- **Tool Usage Tracking**: Monitor which tools are used in each interaction

### Smart Routing
- **Intelligent Task Classification**: Automatically routes requests to appropriate agent workflows
- **Content Analysis**: Sentiment analysis, keyword extraction, text complexity assessment
- **Knowledge Search**: Domain-specific information retrieval (technical, business, science)
- **Data Processing**: Statistical calculations and metrics from numeric data
- **Workflow Guidance**: Step-by-step process assistance

## 🏗️ Architecture

### Backend Components

#### 1. FastAPI WebSocket Server (`mcp_server/streaming.py`)
```python
# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str)

# REST endpoints for session management
@router.get("/streaming/sessions")  # List active sessions
@router.get("/streaming/sessions/{session_id}")  # Get session info
@router.post("/streaming/broadcast")  # Broadcast to all clients
```

#### 2. LangGraph Agent Engine (`mcp_server/langgraph_agent.py`)
```python
# Agent workflow nodes
- router_node: Intelligent request routing
- analyze_content_node: Text analysis and insights
- search_knowledge_node: Information retrieval
- calculate_metrics_node: Data processing
- process_workflow_node: Process guidance
- general_response_node: Fallback responses
```

#### 3. Connection Manager
- Maintains active WebSocket connections
- Handles session state and message history
- Provides broadcasting capabilities
- Manages connection lifecycle

### Frontend Components

#### 1. React Streaming Chat (`ui/src/StreamingChat.js`)
- Real-time WebSocket client
- Modern chat interface with typing indicators
- Message type visualization
- Step-by-step agent progress tracking
- Connection status monitoring

#### 2. Tab-based UI (`ui/src/App.js`)
- Streaming Agent tab for real-time chat
- PDF Workflow tab for existing functionality
- Seamless navigation between features

## 🚀 Getting Started

### 1. Installation

```bash
# Install dependencies
python setup_streaming.py

# Or manually:
pip install -r requirements.txt
cd ui && npm install
```

### 2. Start the Backend

```bash
python -m uvicorn mcp_server.main:app --host 0.0.0.0 --port 8002 --reload
```

### 3. Start the Frontend

```bash
cd ui
npm start
```

### 4. Access the Application

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8002/docs
- **WebSocket Endpoint**: ws://localhost:8002/api/v1/ws/{session_id}

## 🧪 Testing

### Automated Testing
```bash
python test_streaming.py
```

### Manual Testing
1. Open the web interface at http://localhost:3000
2. Click on the "🚀 Streaming Agent" tab
3. Try these example messages:
   - `"Analyze this text: I love this new feature!"`
   - `"Search for information about machine learning"`
   - `"Calculate metrics for: 10, 20, 30, 25, 35"`
   - `"Help me with a workflow for data analysis"`

## 📡 API Reference

### WebSocket Messages

#### Client to Server
```json
{
  "type": "user_message",
  "content": "Your message here",
  "session_id": "uuid-session-id"
}
```

#### Server to Client
```json
{
  "type": "agent_response",
  "content": "Agent's response",
  "session_id": "uuid-session-id",
  "agent_type": "langgraph_advanced",
  "step_info": {
    "step_number": 1,
    "confidence_score": 0.85,
    "tools_used": ["analyze_text_content"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Message Types
- `connection_established`: Initial connection confirmation
- `agent_processing_start`: Agent begins processing
- `agent_step_detailed`: Step-by-step progress updates
- `agent_response`: Final agent response
- `agent_processing_complete`: Processing finished
- `error`: Error messages

### REST Endpoints

#### Get Active Sessions
```http
GET /api/v1/streaming/sessions
```

#### Get Session Info
```http
GET /api/v1/streaming/sessions/{session_id}
```

#### Broadcast Message
```http
POST /api/v1/streaming/broadcast
Content-Type: application/json

{
  "type": "broadcast",
  "content": "Message to all clients",
  "session_id": "system"
}
```

## 🔧 Agent Tools

### 1. Text Analysis Tool
- **Sentiment Analysis**: Positive/negative/neutral sentiment detection
- **Keyword Extraction**: Important terms and frequency analysis
- **Complexity Assessment**: Text difficulty and readability metrics
- **Summarization**: Concise content summaries

### 2. Knowledge Search Tool
- **Domain-Specific Search**: Technical, business, science, general knowledge
- **Contextual Responses**: Relevant information based on query intent
- **Multi-Domain Support**: Cross-domain information retrieval

### 3. Metrics Calculation Tool
- **Basic Statistics**: Mean, median, min, max, count
- **Advanced Metrics**: Standard deviation, variance
- **Financial Calculations**: Growth rates, totals, performance metrics
- **Data Validation**: Input parsing and error handling

### 4. Workflow Processing Tool
- **Process Guidance**: Step-by-step workflow assistance
- **Context Awareness**: Tailored responses based on user context
- **Multi-Step Workflows**: Complex process breakdown

## 🎯 Usage Examples

### Text Analysis
```
User: "Analyze this text: The new streaming feature is absolutely fantastic and works seamlessly!"

Agent Response:
- Sentiment: positive (positive: 2, negative: 0)
- Keywords: streaming(1), feature(1), fantastic(1), seamlessly(1)
- Complexity: medium (avg 8.0 words/sentence)
```

### Data Analysis
```
User: "Calculate metrics for: 85, 92, 78, 95, 88, 91"

Agent Response:
Basic Metrics - Total: 529, Count: 6, Average: 88.17, Min: 78, Max: 95
Statistical Metrics - Mean: 88.17, Median: 89.50, Std Dev: 6.24, Variance: 38.97
Financial Metrics - Total Value: $529.00, Growth Rate: 7.1%, Data Points: 6
```

### Knowledge Search
```
User: "Search for information about WebSockets"

Agent Response:
WebSockets provide full-duplex communication channels over a single TCP connection, 
ideal for real-time applications. They enable bidirectional data flow between 
client and server with minimal overhead.
```

## 🔒 Security Considerations

### CORS Configuration
- Currently set to allow all origins (`"*"`) for development
- **Production**: Configure specific allowed origins

### WebSocket Security
- Session-based connections with unique IDs
- Message validation and error handling
- Connection lifecycle management

### Data Privacy
- No persistent storage of chat messages
- Session data cleared on disconnection
- Local processing of sensitive data

## 🚀 Advanced Features

### Custom Message Types
Extend the agent with custom message types:

```python
# Add to streaming.py
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    # Handle custom message types
    if message_data.get("type") == "custom_action":
        # Process custom logic
        pass
```

### Agent Tool Extensions
Add new tools to the LangGraph agent:

```python
# Add to langgraph_agent.py
@tool
def your_custom_tool(input_data: str) -> str:
    """Your custom tool description"""
    # Tool implementation
    return "Tool result"

# Add to tools list
tools = [analyze_text_content, search_knowledge_base, calculate_metrics, 
         process_workflow_step, your_custom_tool]
```

### Frontend Customization
Extend the React UI with new features:

```javascript
// Add to StreamingChat.js
const handleCustomMessage = (message) => {
  if (message.type === 'custom_response') {
    // Handle custom response type
  }
};
```

## 🐛 Troubleshooting

### Common Issues

#### WebSocket Connection Failed
```
Error: Connection refused
Solution: Ensure backend server is running on port 8002
```

#### Import Errors
```
Error: Module 'langchain' not found
Solution: Run pip install -r requirements.txt
```

#### UI Not Loading
```
Error: Cannot connect to development server
Solution: Run npm install in ui/ directory, then npm start
```

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Optimization

### Backend Optimization
- Connection pooling for multiple clients
- Message queuing for high-throughput scenarios
- Async/await for non-blocking operations

### Frontend Optimization
- Message virtualization for large chat histories
- Debounced input handling
- Optimized re-rendering with React hooks

## 🔮 Future Enhancements

### Planned Features
1. **Persistent Chat History**: Database storage for conversation history
2. **User Authentication**: Secure user sessions and personalization
3. **Agent Customization**: User-configurable agent personalities
4. **File Upload Support**: Process documents and images
5. **Voice Integration**: Speech-to-text and text-to-speech capabilities
6. **Multi-Agent Conversations**: Collaborative agent workflows
7. **Analytics Dashboard**: Usage metrics and performance monitoring

### Integration Opportunities
- **External APIs**: Weather, news, financial data
- **Database Connections**: Real-time data queries
- **Cloud Services**: AWS, Azure, GCP integrations
- **Monitoring**: Prometheus, Grafana dashboards

## 📝 Contributing

To contribute to the streaming functionality:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-streaming-feature`
3. **Make your changes** following the existing patterns
4. **Test thoroughly** using the provided test scripts
5. **Submit a pull request** with detailed description

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comprehensive docstrings
- Include type hints where appropriate
- Write unit tests for new functionality

## 📄 License

This streaming functionality is part of the MCP-A2A project and follows the same licensing terms as the main project.

---

**Happy Streaming! 🚀✨**
