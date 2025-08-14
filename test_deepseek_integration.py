#!/usr/bin/env python3
"""
Test script for DeepSeek API integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_integration import DeepSeekClient, initialize_deepseek_client, query_deepseek, generate_mcqs_with_deepseek
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_client():
    """Test DeepSeek client functionality."""
    print("🧪 Testing DeepSeek API Integration")
    print("=" * 60)
    
    # Check API key availability
    api_key = os.getenv('DEEPSEEK_API_KEY')
    print(f"📋 API Key Available: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("❌ DeepSeek API key not configured")
        print("💡 Please add your token to the .env file as DEEPSEEK_API_KEY")
        print("🔗 Get your token from: https://platform.deepseek.com/api_keys")
        return False
    
    print(f"✅ DeepSeek API key configured: {api_key[:10]}...")
    
    # Initialize client
    print("\n🔧 Initializing DeepSeek client...")
    client = initialize_deepseek_client()
    
    if not client:
        print("❌ Failed to initialize DeepSeek client")
        return False
    
    print("✅ DeepSeek client initialized successfully")
    
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
        
        answer = query_deepseek(client, question, context)
        
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
        
        mcqs = generate_mcqs_with_deepseek(
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
    
    print("\n" + "=" * 60)
    print("🎉 DeepSeek integration test completed successfully!")
    return True

def display_setup_instructions():
    """Display setup instructions for DeepSeek API."""
    print("\n" + "=" * 60)
    print("🔑 DEEPSEEK API SETUP INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. 🌐 Visit: https://platform.deepseek.com/api_keys")
    print("2. 📝 Sign up or log in to your DeepSeek account")
    print("3. ➕ Click 'Create API Key' to generate a new key")
    print("4. 📄 Copy the generated API key (starts with 'sk-')")
    print("5. 📁 Open your .env file in the project directory")
    print("6. ✏️  Add or update the line:")
    print("   DEEPSEEK_API_KEY=your_api_key_here")
    print("7. 🔄 Restart the application")
    print()
    print("💡 DeepSeek API is COMPLETELY FREE!")
    print("🎯 High-quality responses comparable to GPT-4")
    print("📊 Very generous rate limits")
    print("🚀 Perfect for quiz generation and Q&A")
    print()
    print("🔗 Direct link: https://platform.deepseek.com/api_keys")
    print("=" * 60)

def test_model_info():
    """Test model information retrieval."""
    print("\n📊 Testing model information...")
    
    client = DeepSeekClient()
    if client.is_available():
        info = client.get_model_info()
        print("✅ Model information retrieved:")
        for key, value in info.items():
            print(f"   {key}: {value}")
    else:
        print("❌ Client not available for model info test")

if __name__ == "__main__":
    success = test_deepseek_client()
    
    if not success:
        display_setup_instructions()
    else:
        print("\n✅ DeepSeek integration is working correctly!")
        print("🚀 You can now use DeepSeek as your AI provider!")
        
        # Test model info
        test_model_info()
        
        print("\n💡 To use DeepSeek in the app:")
        print("   1. Select 'DeepSeek (Free)' from the AI provider dropdown")
        print("   2. Click 'Initialize AI' button")
        print("   3. Enjoy unlimited, high-quality AI responses!")
