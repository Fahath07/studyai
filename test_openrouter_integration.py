#!/usr/bin/env python3
"""
Test script for OpenRouter DeepSeek integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openrouter_integration import OpenRouterClient, initialize_openrouter_client, query_openrouter_deepseek, generate_mcqs_with_openrouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_client():
    """Test OpenRouter client functionality."""
    print("🧪 Testing OpenRouter DeepSeek Integration")
    print("=" * 70)
    
    # Check API key availability
    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"📋 OpenRouter API Key Available: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("❌ OpenRouter API key not configured")
        print("💡 Please add your token to the .env file as OPENROUTER_API_KEY")
        print("🔗 Get your token from: https://openrouter.ai/keys")
        return False
    
    print(f"✅ OpenRouter API key configured: {api_key[:15]}...")
    
    # Initialize client
    print("\n🔧 Initializing OpenRouter client...")
    client = initialize_openrouter_client()
    
    if not client:
        print("❌ Failed to initialize OpenRouter client")
        return False
    
    print("✅ OpenRouter client initialized successfully")
    print(f"📊 Model: {client.model}")
    print(f"🌐 Base URL: {client.base_url}")
    
    # Test basic response generation
    print("\n💬 Testing basic response generation...")
    try:
        response = client.generate_response(
            prompt="What is artificial intelligence?",
            max_tokens=100,
            temperature=0.7
        )
        
        if response.success:
            print("✅ Basic response generation successful!")
            print(f"📝 Response: {response.content[:100]}...")
            print(f"📊 Usage: {response.usage}")
        else:
            print(f"❌ Basic response generation failed: {response.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error during basic response generation: {e}")
        return False
    
    # Test Q&A functionality
    print("\n❓ Testing Q&A functionality...")
    try:
        context = """
        Python is a high-level programming language known for its simplicity and readability.
        It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
        Python is widely used in web development, data science, artificial intelligence, and automation.
        """
        
        question = "What are the main uses of Python?"
        
        answer = query_openrouter_deepseek(client, context, question)
        
        if answer:
            print("✅ Q&A functionality successful!")
            print(f"📝 Answer: {answer[:150]}...")
        else:
            print("❌ Q&A functionality failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during Q&A test: {e}")
        return False
    
    # Test MCQ generation
    print("\n🧠 Testing MCQ generation...")
    try:
        mcq_context = """
        Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.
        There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.
        Supervised learning uses labeled data to train models, unsupervised learning finds patterns in unlabeled data, and reinforcement learning learns through trial and error.
        """
        
        mcqs = generate_mcqs_with_openrouter(
            client=client,
            context=mcq_context,
            num_questions=2,
            difficulty="medium",
            topic_focus="Machine Learning"
        )
        
        if mcqs:
            print("✅ MCQ generation successful!")
            print(f"📝 Generated MCQs: {mcqs[:200]}...")
        else:
            print("❌ MCQ generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during MCQ generation test: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 OpenRouter DeepSeek integration test completed successfully!")
    return True

def display_setup_instructions():
    """Display setup instructions for OpenRouter API."""
    print("\n" + "=" * 70)
    print("🔑 OPENROUTER API SETUP INSTRUCTIONS")
    print("=" * 70)
    print()
    print("1. 🌐 Visit: https://openrouter.ai/keys")
    print("2. 📝 Sign up or log in to your OpenRouter account")
    print("3. ➕ Click 'Create Key' to generate a new API key")
    print("4. 📄 Copy the generated API key (starts with 'sk-or-')")
    print("5. 📁 Open your .env file in the project directory")
    print("6. ✏️  Add or update the line:")
    print("   OPENROUTER_API_KEY=your_api_key_here")
    print("7. 🔄 Restart the application")
    print()
    print("💡 OpenRouter provides reliable access to DeepSeek!")
    print("🎯 High-quality responses through unified API")
    print("📊 Pay-per-use pricing with free credits")
    print("🚀 Perfect for quiz generation and Q&A")
    print()
    print("🔗 Direct link: https://openrouter.ai/keys")
    print("=" * 70)

def test_model_info():
    """Test model information retrieval."""
    print("\n📊 Testing model information...")
    
    client = OpenRouterClient()
    if client.is_available():
        info = client.get_model_info()
        print("✅ Model information retrieved:")
        for key, value in info.items():
            print(f"   {key}: {value}")
    else:
        print("❌ Client not available for model info test")

def test_deepseek_integration():
    """Test the enhanced DeepSeek integration with OpenRouter fallback."""
    print("\n🔄 Testing Enhanced DeepSeek Integration...")
    print("-" * 50)
    
    try:
        from deepseek_integration import initialize_deepseek_client
        
        client = initialize_deepseek_client()
        if client:
            print("✅ DeepSeek client initialized (via OpenRouter)")
            
            # Check if it's OpenRouter
            if hasattr(client, 'base_url') and 'openrouter' in str(client.base_url):
                print("🎯 Using OpenRouter for DeepSeek access")
            else:
                print("🎯 Using direct DeepSeek API")
                
            return True
        else:
            print("❌ DeepSeek client initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing DeepSeek integration: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_client()
    
    if not success:
        display_setup_instructions()
    else:
        print("\n✅ OpenRouter integration is working correctly!")
        print("🚀 You can now use DeepSeek via OpenRouter!")
        
        # Test model info
        test_model_info()
        
        # Test enhanced DeepSeek integration
        test_deepseek_integration()
        
        print("\n💡 To use OpenRouter DeepSeek in the app:")
        print("   1. Select 'DeepSeek (Free)' from the AI provider dropdown")
        print("   2. Click 'Initialize AI' button")
        print("   3. Enjoy reliable, high-quality AI responses via OpenRouter!")
