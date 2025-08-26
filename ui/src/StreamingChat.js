import React, { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";

const WS_BASE = "ws://localhost:8002";

const styles = {
  container: {
    maxWidth: 900,
    margin: "2rem auto",
    padding: "2rem",
    background: "#fff",
    borderRadius: 16,
    boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
    fontFamily: "'Segoe UI', 'Roboto', 'Arial', sans-serif",
    height: "85vh",
    display: "flex",
    flexDirection: "column",
  },
  header: {
    textAlign: "center",
    marginBottom: "1.5rem",
    borderBottom: "2px solid #e2e8f0",
    paddingBottom: "1rem",
  },
  title: {
    fontSize: 32,
    fontWeight: 700,
    marginBottom: 8,
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    fontSize: 16,
    color: "#64748b",
    marginBottom: 12,
  },
  statusIndicator: {
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    padding: "6px 12px",
    borderRadius: 20,
    fontSize: 14,
    fontWeight: 500,
  },
  connected: {
    background: "#ecfdf5",
    color: "#065f46",
  },
  disconnected: {
    background: "#fef2f2",
    color: "#991b1b",
  },
  connecting: {
    background: "#fef3c7",
    color: "#92400e",
  },
  chatContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  messagesContainer: {
    flex: 1,
    overflowY: "auto",
    padding: "1rem 0",
    marginBottom: "1rem",
    border: "1px solid #e2e8f0",
    borderRadius: 12,
    background: "#f8fafc",
  },
  message: {
    margin: "0.5rem 1rem",
    padding: "12px 16px",
    borderRadius: 12,
    maxWidth: "80%",
    wordWrap: "break-word",
  },
  userMessage: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    marginLeft: "auto",
    textAlign: "right",
  },
  agentMessage: {
    background: "#ffffff",
    color: "#1e293b",
    border: "1px solid #e2e8f0",
    boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
  },
  systemMessage: {
    background: "#f1f5f9",
    color: "#475569",
    fontStyle: "italic",
    textAlign: "center",
    margin: "0.5rem auto",
    maxWidth: "60%",
  },
  stepMessage: {
    background: "#fef7cd",
    color: "#92400e",
    fontSize: 14,
    fontFamily: "monospace",
    border: "1px solid #fbbf24",
  },
  errorMessage: {
    background: "#fef2f2",
    color: "#991b1b",
    border: "1px solid #fca5a5",
  },
  messageHeader: {
    fontSize: 12,
    opacity: 0.7,
    marginBottom: 4,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  messageContent: {
    fontSize: 15,
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
  },
  inputContainer: {
    display: "flex",
    gap: "12px",
    alignItems: "stretch",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    border: "2px solid #e2e8f0",
    borderRadius: 12,
    fontSize: 16,
    outline: "none",
    transition: "border-color 0.2s",
    fontFamily: "inherit",
    resize: "none",
    minHeight: "20px",
    maxHeight: "100px",
  },
  inputFocused: {
    borderColor: "#667eea",
  },
  sendButton: {
    padding: "12px 24px",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    border: "none",
    borderRadius: 12,
    fontSize: 16,
    fontWeight: 600,
    cursor: "pointer",
    transition: "opacity 0.2s",
    minWidth: "80px",
  },
  sendButtonDisabled: {
    opacity: 0.5,
    cursor: "not-allowed",
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    backgroundColor: "currentColor",
  },
  stepInfo: {
    fontSize: 12,
    opacity: 0.8,
    marginTop: 4,
    padding: "4px 8px",
    background: "rgba(0,0,0,0.05)",
    borderRadius: 6,
  },
  toolBadge: {
    display: "inline-block",
    background: "#3b82f6",
    color: "white",
    padding: "2px 8px",
    borderRadius: 12,
    fontSize: 11,
    fontWeight: 500,
    margin: "2px 4px 2px 0",
  },
  confidenceBar: {
    width: "100%",
    height: 4,
    background: "#e2e8f0",
    borderRadius: 2,
    overflow: "hidden",
    marginTop: 4,
  },
  confidenceFill: {
    height: "100%",
    background: "linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%)",
    transition: "width 0.3s ease",
  },
};

function StreamingChat() {
  const [ws, setWs] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [inputFocused, setInputFocused] = useState(false);
  const [sessionId] = useState(() => uuidv4());
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    setConnectionStatus("connecting");
    console.log("Attempting WebSocket connection to:", `${WS_BASE}/api/v1/ws/${sessionId}`);
    
    const websocket = new WebSocket(`${WS_BASE}/api/v1/ws/${sessionId}`);
    
    websocket.onopen = () => {
      console.log("WebSocket connected successfully");
      setConnectionStatus("connected");
      setWs(websocket);
    };
    
    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log("Received message:", message);
        
        const newMessage = {
          id: Date.now() + Math.random(),
          type: message.type,
          content: message.content,
          timestamp: message.timestamp || new Date().toISOString(),
          stepInfo: message.step_info,
          agentType: message.agent_type,
          sender: "agent",
        };
        
        setMessages(prev => [...prev, newMessage]);
      } catch (error) {
        console.error("Error parsing message:", error);
      }
    };
    
    websocket.onclose = (event) => {
      console.log("WebSocket disconnected:", event.code, event.reason);
      setConnectionStatus("disconnected");
      setWs(null);
    };
    
    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      console.error("WebSocket URL:", `${WS_BASE}/api/v1/ws/${sessionId}`);
      setConnectionStatus("disconnected");
    };
  };

  const sendMessage = () => {
    if (!ws || !inputValue.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      type: "user_message",
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
      sender: "user",
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    ws.send(JSON.stringify({
      type: "user_message",
      content: inputValue.trim(),
      session_id: sessionId,
    }));
    
    setInputValue("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMessage = (message) => {
    const isUser = message.sender === "user";
    const isSystem = message.type === "connection_established" || 
                    message.type === "agent_processing_start" || 
                    message.type === "agent_processing_complete";
    const isStep = message.type === "agent_step_detailed";
    const isError = message.type === "error";

    let messageStyle = { ...styles.message };
    
    if (isUser) {
      messageStyle = { ...messageStyle, ...styles.userMessage };
    } else if (isSystem) {
      messageStyle = { ...messageStyle, ...styles.systemMessage };
    } else if (isStep) {
      messageStyle = { ...messageStyle, ...styles.stepMessage };
    } else if (isError) {
      messageStyle = { ...messageStyle, ...styles.errorMessage };
    } else {
      messageStyle = { ...messageStyle, ...styles.agentMessage };
    }

    return (
      <div key={message.id} style={messageStyle}>
        <div style={styles.messageHeader}>
          <span>
            {isUser ? "You" : isStep ? "Agent Step" : isSystem ? "System" : "LangGraph Agent"}
          </span>
          <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
        </div>
        
        <div style={styles.messageContent}>
          {message.content}
        </div>
        
        {message.stepInfo && (
          <div style={styles.stepInfo}>
            {message.stepInfo.step_number && (
              <div>Step: {message.stepInfo.step_number}</div>
            )}
            {message.stepInfo.node_name && (
              <div>Node: {message.stepInfo.node_name}</div>
            )}
            {message.stepInfo.tools_used && message.stepInfo.tools_used.length > 0 && (
              <div>
                Tools: {message.stepInfo.tools_used.map((tool, index) => (
                  <span key={index} style={styles.toolBadge}>{tool}</span>
                ))}
              </div>
            )}
            {message.stepInfo.confidence_score !== undefined && (
              <div>
                Confidence: {(message.stepInfo.confidence_score * 100).toFixed(1)}%
                <div style={styles.confidenceBar}>
                  <div 
                    style={{
                      ...styles.confidenceFill,
                      width: `${message.stepInfo.confidence_score * 100}%`
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const getStatusStyle = () => {
    switch (connectionStatus) {
      case "connected":
        return { ...styles.statusIndicator, ...styles.connected };
      case "connecting":
        return { ...styles.statusIndicator, ...styles.connecting };
      default:
        return { ...styles.statusIndicator, ...styles.disconnected };
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case "connected":
        return "Connected";
      case "connecting":
        return "Connecting...";
      default:
        return "Disconnected";
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.title}>🚀 LangGraph Streaming Agent</div>
        <div style={styles.subtitle}>
          Real-time WebSocket communication with advanced AI workflows
        </div>
        <div style={getStatusStyle()}>
          <div style={styles.statusDot} />
          {getStatusText()}
        </div>
      </div>
      
      <div style={styles.chatContainer}>
        <div style={styles.messagesContainer}>
          {messages.length === 0 && (
            <div style={{ ...styles.message, ...styles.systemMessage }}>
              <div style={styles.messageContent}>
                Welcome! This is an advanced LangGraph agent that can:
                <br />• 🔍 Analyze text content (sentiment, keywords, complexity)
                <br />• 📚 Search knowledge bases across different domains
                <br />• 📊 Calculate metrics and statistics from data
                <br />• ⚙️ Process workflows and procedures
                <br /><br />
                Try asking: "Analyze this text: I love this new feature!" or "Calculate metrics for: 10, 20, 30, 25, 35"
              </div>
            </div>
          )}
          
          {messages.map(renderMessage)}
          <div ref={messagesEndRef} />
        </div>
        
        <div style={styles.inputContainer}>
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setInputFocused(true)}
            onBlur={() => setInputFocused(false)}
            placeholder="Type your message here... (Shift+Enter for new line)"
            style={{
              ...styles.input,
              ...(inputFocused ? styles.inputFocused : {}),
            }}
            disabled={connectionStatus !== "connected"}
          />
          <button
            onClick={sendMessage}
            disabled={connectionStatus !== "connected" || !inputValue.trim()}
            style={{
              ...styles.sendButton,
              ...((connectionStatus !== "connected" || !inputValue.trim()) ? styles.sendButtonDisabled : {}),
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default StreamingChat;
