"""
Advanced LangGraph agent for learning and demonstration purposes
This module implements a sophisticated multi-step agent workflow using LangGraph
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
import operator

# LangGraph and LangChain imports
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.tools import BaseTool, tool
from langchain.callbacks.base import BaseCallbackHandler
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

logger = logging.getLogger("mcp_server.langgraph_agent")

# Define the agent state structure
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    current_step: str
    analysis_results: Dict[str, Any]
    task_context: Dict[str, Any]
    tools_used: List[str]
    session_id: str
    step_count: int
    confidence_score: float
    next_action: Optional[str]

# Advanced tools for the agent
@tool
def analyze_text_content(text: str, analysis_type: str = "sentiment") -> str:
    """
    Analyze text content for various insights.
    
    Args:
        text: The text to analyze
        analysis_type: Type of analysis (sentiment, keywords, summary, complexity)
    """
    logger.info(f"Analyzing text with type: {analysis_type}")
    
    if analysis_type == "sentiment":
        # Mock sentiment analysis
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
        
        text_lower = text.lower()
        pos_count = sum(word in text_lower for word in positive_words)
        neg_count = sum(word in text_lower for word in negative_words)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return f"Sentiment analysis: {sentiment} (positive: {pos_count}, negative: {neg_count})"
    
    elif analysis_type == "keywords":
        # Mock keyword extraction
        words = text.split()
        word_freq = {}
        for word in words:
            cleaned = word.lower().strip(".,!?;:")
            if len(cleaned) > 3:  # Only words longer than 3 characters
                word_freq[cleaned] = word_freq.get(cleaned, 0) + 1
        
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return f"Top keywords: {', '.join([f'{word}({count})' for word, count in top_keywords])}"
    
    elif analysis_type == "summary":
        # Mock summarization
        sentences = text.split(".")
        summary_length = min(2, len(sentences))
        summary = ". ".join(sentences[:summary_length]) + "."
        return f"Summary: {summary}"
    
    elif analysis_type == "complexity":
        # Mock complexity analysis
        word_count = len(text.split())
        sentence_count = len(text.split("."))
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        if avg_words_per_sentence > 20:
            complexity = "high"
        elif avg_words_per_sentence > 10:
            complexity = "medium"
        else:
            complexity = "low"
            
        return f"Text complexity: {complexity} (avg {avg_words_per_sentence:.1f} words/sentence)"
    
    return f"Analysis type '{analysis_type}' not supported"

@tool
def search_knowledge_base(query: str, domain: str = "general") -> str:
    """
    Search a mock knowledge base for information.
    
    Args:
        query: Search query
        domain: Knowledge domain (general, technical, business, science)
    """
    logger.info(f"Searching knowledge base for: {query} in domain: {domain}")
    
    # Mock knowledge base responses
    knowledge_responses = {
        "general": {
            "ai": "Artificial Intelligence is a field of computer science focused on creating systems that can perform tasks typically requiring human intelligence.",
            "machine learning": "Machine Learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
            "langchain": "LangChain is a framework for developing applications powered by language models, focusing on data-aware and agentic applications.",
            "default": f"General knowledge about '{query}': This is a broad topic with multiple applications and considerations."
        },
        "technical": {
            "websocket": "WebSockets provide full-duplex communication channels over a single TCP connection, ideal for real-time applications.",
            "fastapi": "FastAPI is a modern, high-performance web framework for building APIs with Python, featuring automatic OpenAPI documentation.",
            "react": "React is a JavaScript library for building user interfaces, particularly single-page applications with component-based architecture.",
            "default": f"Technical information about '{query}': This involves implementation details and best practices specific to the technology stack."
        },
        "business": {
            "strategy": "Business strategy involves defining long-term goals and determining the best approach to achieve competitive advantage.",
            "automation": "Business process automation uses technology to streamline operations, reduce costs, and improve efficiency.",
            "default": f"Business insights about '{query}': Consider the impact on operations, costs, and stakeholder value."
        },
        "science": {
            "data": "Data science combines statistical methods, algorithms, and domain expertise to extract insights from structured and unstructured data.",
            "research": "Scientific research follows systematic methodologies to investigate hypotheses and contribute to knowledge advancement.",
            "default": f"Scientific perspective on '{query}': This involves empirical analysis and evidence-based conclusions."
        }
    }
    
    domain_knowledge = knowledge_responses.get(domain, knowledge_responses["general"])
    
    # Find best match
    query_lower = query.lower()
    for key, response in domain_knowledge.items():
        if key != "default" and key in query_lower:
            return response
    
    return domain_knowledge["default"]

@tool
def calculate_metrics(data_points: str, metric_type: str = "basic") -> str:
    """
    Calculate various metrics from data points.
    
    Args:
        data_points: Comma-separated numeric values
        metric_type: Type of metrics (basic, statistical, financial)
    """
    logger.info(f"Calculating {metric_type} metrics for data: {data_points}")
    
    try:
        # Parse data points
        values = [float(x.strip()) for x in data_points.split(",") if x.strip()]
        
        if not values:
            return "No valid numeric data points provided"
        
        if metric_type == "basic":
            total = sum(values)
            count = len(values)
            average = total / count
            minimum = min(values)
            maximum = max(values)
            
            return f"Basic metrics - Total: {total}, Count: {count}, Average: {average:.2f}, Min: {minimum}, Max: {maximum}"
        
        elif metric_type == "statistical":
            import statistics
            mean = statistics.mean(values)
            median = statistics.median(values)
            
            if len(values) > 1:
                std_dev = statistics.stdev(values)
                variance = statistics.variance(values)
                return f"Statistical metrics - Mean: {mean:.2f}, Median: {median:.2f}, Std Dev: {std_dev:.2f}, Variance: {variance:.2f}"
            else:
                return f"Statistical metrics - Mean: {mean:.2f}, Median: {median:.2f} (single value)"
        
        elif metric_type == "financial":
            # Mock financial calculations
            total_value = sum(values)
            growth_rate = ((values[-1] - values[0]) / values[0] * 100) if len(values) > 1 and values[0] != 0 else 0
            
            return f"Financial metrics - Total Value: ${total_value:.2f}, Growth Rate: {growth_rate:.1f}%, Data Points: {len(values)}"
        
    except ValueError as e:
        return f"Error parsing data points: {e}"
    except Exception as e:
        return f"Error calculating metrics: {e}"

@tool
def process_workflow_step(step_name: str, context: str = "") -> str:
    """
    Process a specific workflow step with context.
    
    Args:
        step_name: Name of the workflow step
        context: Additional context for the step
    """
    logger.info(f"Processing workflow step: {step_name}")
    
    workflow_steps = {
        "data_collection": "Data collection phase: Gathering relevant information from various sources and validating data quality.",
        "analysis": "Analysis phase: Processing collected data using appropriate analytical methods and identifying patterns.",
        "insight_generation": "Insight generation: Deriving meaningful conclusions and actionable insights from the analysis.",
        "recommendation": "Recommendation phase: Formulating specific recommendations based on insights and business context.",
        "validation": "Validation phase: Reviewing recommendations for feasibility and potential impact.",
        "implementation": "Implementation planning: Creating detailed steps for putting recommendations into action."
    }
    
    base_response = workflow_steps.get(step_name, f"Processing custom workflow step: {step_name}")
    
    if context:
        return f"{base_response} Context: {context}"
    
    return base_response

# Available tools for the agent
tools = [analyze_text_content, search_knowledge_base, calculate_metrics, process_workflow_step]

# Agent workflow nodes
async def router_node(state: AgentState) -> AgentState:
    """Route the conversation to appropriate next step"""
    logger.info(f"Router node processing for session {state['session_id']}")
    
    # Get the last message
    messages = state["messages"]
    if not messages:
        state["next_action"] = "clarify"
        return state
    
    last_message = messages[-1]
    content = last_message.content.lower()
    
    # Simple routing logic based on content
    if any(word in content for word in ["analyze", "analysis", "sentiment", "keywords"]):
        state["next_action"] = "analyze_content"
    elif any(word in content for word in ["search", "find", "knowledge", "information"]):
        state["next_action"] = "search_knowledge"
    elif any(word in content for word in ["calculate", "metrics", "numbers", "data"]):
        state["next_action"] = "calculate_metrics"
    elif any(word in content for word in ["workflow", "process", "step", "procedure"]):
        state["next_action"] = "process_workflow"
    else:
        state["next_action"] = "general_response"
    
    state["current_step"] = "routing_completed"
    state["step_count"] = state.get("step_count", 0) + 1
    
    logger.info(f"Routed to action: {state['next_action']}")
    return state

async def analyze_content_node(state: AgentState) -> AgentState:
    """Analyze content using appropriate tools"""
    logger.info(f"Analyzing content for session {state['session_id']}")
    
    messages = state["messages"]
    user_content = messages[-1].content if messages else ""
    
    # Perform multiple types of analysis
    analyses = []
    for analysis_type in ["sentiment", "keywords", "complexity"]:
        result = analyze_text_content.invoke({"text": user_content, "analysis_type": analysis_type})
        analyses.append(result)
    
    state["tools_used"] = state.get("tools_used", []) + ["analyze_text_content"]
    state["analysis_results"]["content_analysis"] = analyses
    
    # Generate comprehensive response
    analysis_summary = "\n".join(analyses)
    response = f"I've analyzed your content from multiple perspectives:\n\n{analysis_summary}\n\nWould you like me to dive deeper into any specific aspect?"
    
    state["messages"].append(AIMessage(content=response))
    state["current_step"] = "content_analysis_completed"
    state["confidence_score"] = 0.85
    state["step_count"] = state.get("step_count", 0) + 1
    
    return state

async def search_knowledge_node(state: AgentState) -> AgentState:
    """Search knowledge base for relevant information"""
    logger.info(f"Searching knowledge for session {state['session_id']}")
    
    messages = state["messages"]
    user_content = messages[-1].content if messages else ""
    
    # Extract potential search terms and domains
    content_lower = user_content.lower()
    
    # Determine domain
    domain = "general"
    if any(word in content_lower for word in ["technical", "code", "programming", "api"]):
        domain = "technical"
    elif any(word in content_lower for word in ["business", "strategy", "market"]):
        domain = "business"
    elif any(word in content_lower for word in ["research", "study", "data", "science"]):
        domain = "science"
    
    # Search knowledge base
    search_result = search_knowledge_base.invoke({"query": user_content, "domain": domain})
    
    state["tools_used"] = state.get("tools_used", []) + ["search_knowledge_base"]
    state["analysis_results"]["knowledge_search"] = {
        "query": user_content,
        "domain": domain,
        "result": search_result
    }
    
    response = f"Based on my knowledge search in the {domain} domain:\n\n{search_result}\n\nWould you like me to search in a different domain or provide more specific information?"
    
    state["messages"].append(AIMessage(content=response))
    state["current_step"] = "knowledge_search_completed"
    state["confidence_score"] = 0.75
    state["step_count"] = state.get("step_count", 0) + 1
    
    return state

async def calculate_metrics_node(state: AgentState) -> AgentState:
    """Calculate metrics from provided data"""
    logger.info(f"Calculating metrics for session {state['session_id']}")
    
    messages = state["messages"]
    user_content = messages[-1].content if messages else ""
    
    # Extract numbers from the content
    import re
    numbers = re.findall(r'-?\d+(?:\.\d+)?', user_content)
    
    if not numbers:
        response = "I didn't find any numeric data in your message. Please provide some numbers (comma-separated) for me to analyze. For example: '10, 20, 30, 25, 35'"
        state["messages"].append(AIMessage(content=response))
        state["current_step"] = "metrics_calculation_failed"
        return state
    
    data_points = ",".join(numbers)
    
    # Calculate different types of metrics
    metrics_results = []
    for metric_type in ["basic", "statistical", "financial"]:
        try:
            result = calculate_metrics.invoke({"data_points": data_points, "metric_type": metric_type})
            metrics_results.append(f"**{metric_type.title()} Metrics:**\n{result}")
        except Exception as e:
            logger.error(f"Error calculating {metric_type} metrics: {e}")
    
    state["tools_used"] = state.get("tools_used", []) + ["calculate_metrics"]
    state["analysis_results"]["metrics"] = {
        "data_points": data_points,
        "results": metrics_results
    }
    
    metrics_summary = "\n\n".join(metrics_results)
    response = f"I've analyzed your numeric data:\n\n{metrics_summary}\n\nWould you like me to perform additional calculations or provide insights about these metrics?"
    
    state["messages"].append(AIMessage(content=response))
    state["current_step"] = "metrics_calculation_completed"
    state["confidence_score"] = 0.90
    state["step_count"] = state.get("step_count", 0) + 1
    
    return state

async def process_workflow_node(state: AgentState) -> AgentState:
    """Process workflow-related requests"""
    logger.info(f"Processing workflow for session {state['session_id']}")
    
    messages = state["messages"]
    user_content = messages[-1].content if messages else ""
    
    # Identify workflow steps mentioned
    workflow_keywords = {
        "data": "data_collection",
        "collect": "data_collection",
        "analyze": "analysis",
        "analysis": "analysis",
        "insight": "insight_generation",
        "recommend": "recommendation",
        "validate": "validation",
        "implement": "implementation"
    }
    
    content_lower = user_content.lower()
    identified_steps = []
    
    for keyword, step in workflow_keywords.items():
        if keyword in content_lower:
            identified_steps.append(step)
    
    if not identified_steps:
        identified_steps = ["analysis"]  # Default step
    
    # Process each identified step
    workflow_results = []
    for step in set(identified_steps):  # Remove duplicates
        result = process_workflow_step.invoke({"step_name": step, "context": user_content})
        workflow_results.append(f"**{step.replace('_', ' ').title()}:**\n{result}")
    
    state["tools_used"] = state.get("tools_used", []) + ["process_workflow_step"]
    state["analysis_results"]["workflow"] = {
        "identified_steps": identified_steps,
        "results": workflow_results
    }
    
    workflow_summary = "\n\n".join(workflow_results)
    response = f"I've processed your workflow request:\n\n{workflow_summary}\n\nWould you like me to elaborate on any specific step or suggest next actions?"
    
    state["messages"].append(AIMessage(content=response))
    state["current_step"] = "workflow_processing_completed"
    state["confidence_score"] = 0.80
    state["step_count"] = state.get("step_count", 0) + 1
    
    return state

async def general_response_node(state: AgentState) -> AgentState:
    """Handle general conversation"""
    logger.info(f"Generating general response for session {state['session_id']}")
    
    messages = state["messages"]
    user_content = messages[-1].content if messages else ""
    
    # Generate a helpful general response
    response = f"""I understand you're asking about: "{user_content}"

I'm an advanced LangGraph agent that can help you with:

🔍 **Content Analysis**: Sentiment analysis, keyword extraction, text summarization
📚 **Knowledge Search**: Information lookup across different domains (technical, business, science)
📊 **Data Analysis**: Calculate metrics and statistics from numeric data
⚙️ **Workflow Processing**: Guide you through structured processes and procedures

To get started, try asking me to:
- "Analyze this text: [your text here]"
- "Search for information about [topic]"
- "Calculate metrics for these numbers: 10, 20, 30, 25"
- "Help me with a workflow for [your process]"

What would you like me to help you with?"""
    
    state["messages"].append(AIMessage(content=response))
    state["current_step"] = "general_response_completed"
    state["confidence_score"] = 0.70
    state["step_count"] = state.get("step_count", 0) + 1
    
    return state

def should_continue(state: AgentState) -> str:
    """Determine if the workflow should continue"""
    # For this demo, we'll end after each response
    # In a more complex scenario, you might continue based on confidence score or user intent
    return "end"

def route_to_action(state: AgentState) -> str:
    """Route to the appropriate action based on next_action"""
    return state.get("next_action", "general_response")

# Create the LangGraph workflow
def create_advanced_agent():
    """Create an advanced LangGraph agent workflow"""
    
    # Initialize the workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("analyze_content", analyze_content_node)
    workflow.add_node("search_knowledge", search_knowledge_node)
    workflow.add_node("calculate_metrics", calculate_metrics_node)
    workflow.add_node("process_workflow", process_workflow_node)
    workflow.add_node("general_response", general_response_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        route_to_action,
        {
            "analyze_content": "analyze_content",
            "search_knowledge": "search_knowledge",
            "calculate_metrics": "calculate_metrics",
            "process_workflow": "process_workflow",
            "general_response": "general_response"
        }
    )
    
    # Add edges to end
    workflow.add_conditional_edges("analyze_content", should_continue, {"end": END})
    workflow.add_conditional_edges("search_knowledge", should_continue, {"end": END})
    workflow.add_conditional_edges("calculate_metrics", should_continue, {"end": END})
    workflow.add_conditional_edges("process_workflow", should_continue, {"end": END})
    workflow.add_conditional_edges("general_response", should_continue, {"end": END})
    
    return workflow.compile()

# Function to initialize agent state
def initialize_agent_state(session_id: str, user_message: str) -> AgentState:
    """Initialize agent state for a new conversation"""
    return AgentState(
        messages=[HumanMessage(content=user_message)],
        current_step="initialized",
        analysis_results={},
        task_context={},
        tools_used=[],
        session_id=session_id,
        step_count=0,
        confidence_score=0.0,
        next_action=None
    )
