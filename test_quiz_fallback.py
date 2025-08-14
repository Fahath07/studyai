#!/usr/bin/env python3
"""
Test script for quiz generation fallback mechanism
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz_generator import generate_fallback_questions

def test_fallback_generation():
    """Test the fallback question generation."""
    print("🧪 Testing Quiz Fallback Generation")
    print("=" * 50)
    
    # Sample context from Java/Python content
    context = """
    Java is a programming language that uses classes and objects. 
    Variables store data values. Methods define behavior. 
    Arrays hold multiple values. Loops repeat code execution.
    Python uses keywords like def, class, import, return.
    Functions are defined with def keyword.
    Data structures include lists, dictionaries, tuples.
    Exception handling uses try-except blocks.
    """
    
    # Test fallback generation
    print("Generating fallback questions...")
    questions = generate_fallback_questions(context, num_questions=5, difficulty="medium")
    
    print(f"\n✅ Generated {len(questions)} fallback questions:")
    print("-" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. {question.question}")
        for j, option in enumerate(question.options, 1):
            marker = "✓" if option.is_correct else " "
            print(f"   {j}. [{marker}] {option.text}")
        print(f"   Topic: {question.topic}")
        print(f"   Difficulty: {question.difficulty}")
        print(f"   Explanation: {question.explanation}")
    
    return len(questions) > 0

if __name__ == "__main__":
    success = test_fallback_generation()
    if success:
        print("\n🎉 Fallback generation test passed!")
    else:
        print("\n❌ Fallback generation test failed!")
