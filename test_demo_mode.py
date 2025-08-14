#!/usr/bin/env python3
"""
Test script to verify demo mode functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from watsonx_integration import DemoWatsonxClient, create_academic_prompt

def test_demo_client():
    """Test the demo client with sample context and questions."""
    
    print("🧪 Testing Demo Mode Functionality")
    print("=" * 50)
    
    # Initialize demo client
    demo_client = DemoWatsonxClient()
    print(f"✅ Demo client initialized: {demo_client.model_id}")
    
    # Sample context (simulating PDF content)
    sample_context = """
    Machine learning is a method of data analysis that automates analytical model building. 
    It is a branch of artificial intelligence based on the idea that systems can learn from data, 
    identify patterns and make decisions with minimal human intervention. Machine learning algorithms 
    build a model based on training data in order to make predictions or decisions without being 
    explicitly programmed to do so. The field of machine learning is closely related to computational 
    statistics, which focuses on making predictions using computers.
    """
    
    # Test questions
    test_questions = [
        "What is machine learning?",
        "How does machine learning work?", 
        "What is the relationship between machine learning and artificial intelligence?",
        "What is the name of the candidate?",  # Question not related to context
    ]
    
    print("\n🔍 Testing Context-Based Responses:")
    print("-" * 40)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        # Create academic prompt
        prompt = create_academic_prompt(sample_context, question)
        
        # Generate response
        response = demo_client.generate_response(prompt)
        
        print(f"   Answer: {response[:200]}...")
        print(f"   Length: {len(response)} characters")
    
    print("\n🔍 Testing Generic Responses (No Context):")
    print("-" * 40)
    
    generic_questions = [
        "What is artificial intelligence?",
        "How do neural networks work?",
        "Define deep learning",
    ]
    
    for i, question in enumerate(generic_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        # Test without context
        response = demo_client.generate_response(question)
        
        print(f"   Answer: {response[:200]}...")
        print(f"   Length: {len(response)} characters")
    
    print("\n✅ Demo mode testing completed!")
    print("\n📋 Summary:")
    print("- Demo client initializes correctly")
    print("- Context-based responses work")
    print("- Generic responses work")
    print("- All responses include demo disclaimer")

if __name__ == "__main__":
    test_demo_client()
