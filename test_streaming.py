#!/usr/bin/env python3
"""
Test script for WebSocket streaming functionality
"""

import asyncio
import websockets
import json
import uuid
from datetime import datetime

async def test_websocket_connection():
    """Test basic WebSocket connection and message exchange"""
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8002/api/v1/ws/{session_id}"
    
    print(f"🔌 Testing WebSocket connection to: {uri}")
    print(f"📋 Session ID: {session_id}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established")
            
            # Wait for welcome message
            welcome_message = await websocket.recv()
            welcome_data = json.loads(welcome_message)
            print(f"📨 Welcome message: {welcome_data['content']}")
            
            # Test messages to send
            test_messages = [
                "Hello, I'm testing the LangGraph agent!",
                "Analyze this text: I love this new streaming feature!",
                "Search for information about machine learning",
                "Calculate metrics for: 10, 20, 30, 25, 35",
                "Help me with a workflow for data analysis"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n📤 Sending test message {i}: {message}")
                
                # Send message
                await websocket.send(json.dumps({
                    "type": "user_message",
                    "content": message,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Receive responses
                response_count = 0
                timeout_count = 0
                max_timeout = 5  # Maximum timeouts before moving to next message
                
                while response_count < 10 and timeout_count < max_timeout:  # Expect multiple responses
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        response_data = json.loads(response)
                        response_count += 1
                        
                        print(f"📥 Response {response_count} ({response_data['type']}): {response_data['content'][:100]}...")
                        
                        # Break if we get a completion message
                        if response_data['type'] == 'agent_processing_complete':
                            break
                            
                    except asyncio.TimeoutError:
                        timeout_count += 1
                        print(f"⏰ Timeout {timeout_count}/{max_timeout} waiting for response")
                        
                        if timeout_count >= max_timeout:
                            print("⏭️  Moving to next test message due to timeout")
                            break
                
                # Wait a bit before next message
                await asyncio.sleep(2)
            
            print("\n✅ All test messages sent successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Make sure the server is running on localhost:8002")
        return False
    except Exception as e:
        print(f"❌ Error during WebSocket test: {e}")
        return False
    
    return True

async def test_rest_endpoints():
    """Test REST endpoints for session management"""
    import httpx
    
    print("\n🌐 Testing REST endpoints...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test getting active sessions
            response = await client.get("http://localhost:8002/api/v1/streaming/sessions")
            
            if response.status_code == 200:
                sessions = response.json()
                print(f"✅ Found {len(sessions)} active sessions")
                for session in sessions:
                    print(f"   📋 Session {session['session_id'][:8]}... - Status: {session['status']}")
            else:
                print(f"❌ Failed to get sessions: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error testing REST endpoints: {e}")
        return False
    
    return True

def main():
    print("🧪 MCP-A2A WebSocket Streaming Test")
    print("=" * 40)
    print("Make sure the server is running with:")
    print("python -m uvicorn mcp_server.main:app --host 0.0.0.0 --port 8002 --reload")
    print("=" * 40)
    
    try:
        # Test WebSocket functionality
        asyncio.run(test_websocket_connection())
        
        # Test REST endpoints
        asyncio.run(test_rest_endpoints())
        
        print("\n🎉 All tests completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
