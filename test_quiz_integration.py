#!/usr/bin/env python3
"""
Test script for complete quiz integration with fallback
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz_generator import generate_mcqs_with_ai, generate_fallback_questions
from watsonx_integration import initialize_watsonx_client

def test_quiz_with_demo_client():
    """Test quiz generation with demo Watsonx client."""
    print("🧪 Testing Quiz Generation with Demo Client")
    print("=" * 60)
    
    # Initialize demo Watsonx client
    print("Initializing demo Watsonx client...")
    demo_client = initialize_watsonx_client()
    
    if not demo_client:
        print("❌ Failed to initialize demo client")
        return False
    
    print(f"✅ Demo client initialized: {type(demo_client).__name__}")
    
    # Sample context from Java/Python content
    context = """
    Java is an object-oriented programming language. Classes define the structure 
    and behavior of objects. Variables store data values and can be of different types.
    Methods define the behavior of a class. Arrays are used to store multiple values.
    Loops like for and while are used for repetitive execution.
    
    Python uses keywords like def, class, import, return, if, else, while, for.
    Functions are defined using the def keyword. Data structures include lists, 
    dictionaries, tuples, and sets. Exception handling uses try-except blocks.
    """
    
    # Test quiz generation
    print("\nGenerating quiz with demo client...")
    questions = generate_mcqs_with_ai(demo_client, context, num_questions=3, difficulty="medium")
    
    if questions:
        print(f"\n✅ Generated {len(questions)} questions:")
        print("-" * 60)
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question.question}")
            for j, option in enumerate(question.options, 1):
                marker = "✓" if option.is_correct else " "
                print(f"   {j}. [{marker}] {option.text}")
            print(f"   Topic: {question.topic}")
            print(f"   Difficulty: {question.difficulty}")
            if question.explanation:
                print(f"   Explanation: {question.explanation}")
        
        return True
    else:
        print("❌ No questions generated")
        return False

def test_direct_fallback():
    """Test direct fallback generation."""
    print("\n🧪 Testing Direct Fallback Generation")
    print("=" * 60)
    
    context = """
    Programming concepts include variables, functions, classes, objects, arrays,
    loops, conditions, algorithms, data structures, types, keywords, syntax,
    parameters, return values, imports, libraries, exceptions, errors, debugging,
    compilation, and execution.
    """
    
    questions = generate_fallback_questions(context, num_questions=3, difficulty="medium")
    
    if questions:
        print(f"\n✅ Generated {len(questions)} fallback questions:")
        print("-" * 60)
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question.question}")
            for j, option in enumerate(question.options, 1):
                marker = "✓" if option.is_correct else " "
                print(f"   {j}. [{marker}] {option.text}")
            print(f"   Topic: {question.topic}")
            print(f"   Difficulty: {question.difficulty}")
            if question.explanation:
                print(f"   Explanation: {question.explanation}")
        
        return True
    else:
        print("❌ No fallback questions generated")
        return False

if __name__ == "__main__":
    print("🎯 Testing Complete Quiz Integration")
    print("=" * 80)
    
    success1 = test_quiz_with_demo_client()
    success2 = test_direct_fallback()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("🎉 All quiz integration tests passed!")
        print("\n📋 Summary:")
        print("✅ Demo client quiz generation works")
        print("✅ Fallback question generation works")
        print("✅ Quiz system is ready for use!")
    else:
        print("❌ Some tests failed!")
        if not success1:
            print("❌ Demo client quiz generation failed")
        if not success2:
            print("❌ Fallback generation failed")
