#!/usr/bin/env python3
"""
Test script for dynamic quiz generation with different difficulties and topics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz_generator import generate_fallback_questions

def test_dynamic_generation():
    """Test dynamic question generation with different parameters."""
    print("🧪 Testing Dynamic Quiz Generation")
    print("=" * 60)
    
    # Sample context with programming content
    context = """
    Java is an object-oriented programming language that uses classes and objects.
    Variables store data values and can be of different types like int, string, boolean.
    Methods define behavior and can have parameters and return values.
    Arrays store multiple values of the same type. Lists are dynamic data structures.
    Loops like for and while are used for repetitive execution.
    Algorithms are step-by-step procedures for solving problems.
    Data structures organize and store data efficiently.
    Trees are hierarchical data structures with nodes and edges.
    Graphs consist of vertices and edges representing relationships.
    Sorting algorithms arrange data in a specific order.
    Search algorithms find specific elements in data structures.
    """
    
    # Test different difficulties
    difficulties = ["easy", "medium", "hard"]
    topics = ["", "programming", "data structures", "algorithms"]
    
    for difficulty in difficulties:
        print(f"\n🎯 Testing {difficulty.upper()} difficulty:")
        print("-" * 40)
        
        for topic in topics:
            topic_label = topic if topic else "general"
            print(f"\n📚 Topic: {topic_label}")
            
            # Generate questions
            questions = generate_fallback_questions(
                context, 
                num_questions=3, 
                difficulty=difficulty, 
                topic_focus=topic
            )
            
            if questions:
                for i, question in enumerate(questions, 1):
                    print(f"\n{i}. {question.question}")
                    for j, option in enumerate(question.options, 1):
                        marker = "✓" if option.is_correct else " "
                        print(f"   {j}. [{marker}] {option.text}")
                    print(f"   📂 Topic: {question.topic}")
                    print(f"   📊 Difficulty: {question.difficulty}")
            else:
                print("   ❌ No questions generated")
    
    print("\n" + "=" * 60)
    print("🎉 Dynamic generation test completed!")

def test_randomness():
    """Test that questions change between generations."""
    print("\n🔄 Testing Question Randomness")
    print("=" * 60)
    
    context = """
    Programming involves writing code using variables, functions, and classes.
    Data structures like arrays, lists, and trees organize information.
    Algorithms solve problems through step-by-step procedures.
    """
    
    # Generate multiple sets of questions
    question_sets = []
    for i in range(3):
        questions = generate_fallback_questions(
            context, 
            num_questions=2, 
            difficulty="medium", 
            topic_focus="programming"
        )
        question_texts = [q.question for q in questions]
        question_sets.append(question_texts)
        
        print(f"\nGeneration {i+1}:")
        for j, text in enumerate(question_texts, 1):
            print(f"  {j}. {text}")
    
    # Check for differences
    all_same = all(set1 == question_sets[0] for set1 in question_sets[1:])
    
    if all_same:
        print("\n⚠️ Questions are identical across generations")
    else:
        print("\n✅ Questions vary between generations (good!)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_dynamic_generation()
    test_randomness()
