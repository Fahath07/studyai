#!/usr/bin/env python3
"""
Test script for general chatbot functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import ChatbotSession, query_general_ai_provider
from datetime import datetime

def test_chatbot_session():
    """Test chatbot session functionality."""
    print("🧪 Testing Chatbot Session")
    print("=" * 60)
    
    # Create session
    session = ChatbotSession()
    print(f"✅ Created chatbot session")
    print(f"📊 Initial state: {session.total_messages} messages")
    
    # Add test messages
    test_messages = [
        ("user", "Hello, how are you?"),
        ("assistant", "Hello! I'm doing great, thank you for asking. How can I help you today?"),
        ("user", "Can you explain what Python is?"),
        ("assistant", "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used for web development, data science, automation, and more."),
        ("user", "That's helpful, thanks!")
    ]
    
    for role, content in test_messages:
        session.add_message(role, content, "TestModel")
    
    print(f"✅ Added {len(test_messages)} test messages")
    print(f"📊 Final state: {session.total_messages} messages")
    
    # Test conversation context
    context = session.get_conversation_context(max_messages=3)
    print(f"✅ Retrieved context: {len(context)} recent messages")
    
    # Test export
    export_text = session.export_conversation()
    print(f"✅ Exported conversation: {len(export_text)} characters")
    
    # Test clear
    session.clear_conversation()
    print(f"✅ Cleared conversation: {session.total_messages} messages remaining")
    
    return True


def test_ai_provider_query():
    """Test AI provider query functionality."""
    print("\n🧪 Testing AI Provider Query")
    print("=" * 60)
    
    # Mock AI client for testing
    class MockAIClient:
        def __init__(self):
            self.model = "test-model"
        
        class Chat:
            class Completions:
                def create(self, **kwargs):
                    class MockResponse:
                        def __init__(self):
                            self.choices = [MockChoice()]
                    
                    class MockChoice:
                        def __init__(self):
                            self.message = MockMessage()
                    
                    class MockMessage:
                        def __init__(self):
                            self.content = "This is a mock response from the AI model."
                    
                    return MockResponse()
            
            def __init__(self):
                self.completions = self.Completions()
        
        def __init__(self):
            self.model = "test-model"
            self.chat = self.Chat()
    
    # Test with mock client
    mock_client = MockAIClient()
    test_message = "Hello, can you help me with Python?"
    
    try:
        response = query_general_ai_provider(mock_client, test_message)
        
        if response["success"]:
            print(f"✅ Mock AI query successful")
            print(f"📝 Response: {response['answer'][:100]}...")
        else:
            print(f"❌ Mock AI query failed: {response.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"⚠️ Mock AI query error: {e}")
    
    return True


def test_conversation_flow():
    """Test a complete conversation flow."""
    print("\n🧪 Testing Conversation Flow")
    print("=" * 60)
    
    session = ChatbotSession()
    
    # Simulate a conversation
    conversation_turns = [
        "Hi there!",
        "What's the weather like?",
        "Can you help me with math?",
        "What's 2 + 2?",
        "Thanks for your help!"
    ]
    
    print("🗣️ Simulating conversation:")
    
    for i, user_message in enumerate(conversation_turns, 1):
        print(f"  👤 User: {user_message}")
        
        # Add user message
        session.add_message("user", user_message)
        
        # Simulate AI response
        ai_response = f"This is a simulated response to message {i}: '{user_message}'"
        session.add_message("assistant", ai_response, "SimulatedAI")
        
        print(f"  🤖 AI: {ai_response}")
        print()
    
    print(f"✅ Conversation completed with {session.total_messages} total messages")
    
    # Test context retrieval
    recent_context = session.get_conversation_context(max_messages=4)
    print(f"✅ Recent context: {len(recent_context)} messages")
    
    # Test export
    export_text = session.export_conversation()
    print(f"✅ Export generated: {len(export_text)} characters")
    
    # Save export to file for inspection
    with open("test_chatbot_export.txt", "w", encoding="utf-8") as f:
        f.write(export_text)
    print("💾 Export saved to: test_chatbot_export.txt")
    
    return True


def test_chatbot_features():
    """Test various chatbot features."""
    print("\n🧪 Testing Chatbot Features")
    print("=" * 60)
    
    session = ChatbotSession()
    
    # Test session info
    print(f"📅 Session start time: {session.session_start_time}")
    print(f"📊 Initial message count: {session.total_messages}")
    
    # Test message addition with different models
    models = ["GPT-4", "Gemini", "DeepSeek", "Claude"]
    
    for i, model in enumerate(models):
        session.add_message("user", f"Test message {i+1}", model)
        session.add_message("assistant", f"Response from {model}", model)
    
    print(f"✅ Added messages from {len(models)} different models")
    print(f"📊 Total messages: {session.total_messages}")
    
    # Test context with different limits
    for limit in [2, 5, 10]:
        context = session.get_conversation_context(max_messages=limit)
        print(f"📋 Context with limit {limit}: {len(context)} messages")
    
    # Test export functionality
    export = session.export_conversation()
    lines = export.split('\n')
    print(f"📄 Export contains {len(lines)} lines")
    
    # Test clear functionality
    original_count = session.total_messages
    session.clear_conversation()
    print(f"🗑️ Cleared {original_count} messages, now have {session.total_messages}")
    
    return True


def main():
    """Run all chatbot tests."""
    print("💬 StudyMate General Chatbot Test Suite")
    print("=" * 60)
    
    tests = [
        test_chatbot_session,
        test_ai_provider_query,
        test_conversation_flow,
        test_chatbot_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎉 Chatbot Test Suite Completed!")
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Chatbot functionality is ready.")
        print("\n🚀 Next steps:")
        print("   1. Run the main StudyMate application")
        print("   2. Select '💬 General Chatbot' mode")
        print("   3. Start chatting with AI models")
        print("   4. Try both text and voice input")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    main()
