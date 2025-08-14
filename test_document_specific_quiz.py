#!/usr/bin/env python3
"""
Test script to verify document-specific quiz generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz_generator import generate_fallback_questions, create_mcq_prompt_openai, create_mcq_prompt_gemini

def test_document_specific_generation():
    """Test that quiz generation is specific to document content."""
    print("🧪 Testing Document-Specific Quiz Generation")
    print("=" * 60)
    
    # Test with Java-specific content
    java_content = """
    Java is an object-oriented programming language. Classes are blueprints for objects.
    Variables in Java can be int, String, boolean, double. Methods define behavior.
    Inheritance allows classes to inherit from other classes using extends keyword.
    Polymorphism enables objects to take multiple forms. Encapsulation hides data.
    Arrays store multiple values of same type. ArrayList is dynamic array.
    Exception handling uses try-catch blocks. Finally block always executes.
    """
    
    print("\n📄 Testing with Java Document Content:")
    print("-" * 40)
    
    java_questions = generate_fallback_questions(
        java_content, 
        num_questions=3, 
        difficulty="medium", 
        topic_focus="Java"
    )
    
    print(f"Generated {len(java_questions)} Java-specific questions:")
    for i, question in enumerate(java_questions, 1):
        print(f"\n{i}. {question.question}")
        print(f"   Topic: {question.topic}")
        print(f"   Difficulty: {question.difficulty}")
    
    # Test with Python-specific content
    python_content = """
    Python is a high-level programming language. Functions are defined with def keyword.
    Variables don't need type declaration. Lists are ordered collections [1, 2, 3].
    Dictionaries store key-value pairs {'key': 'value'}. Tuples are immutable (1, 2, 3).
    Loops include for and while. List comprehensions [x for x in range(10)].
    Classes use class keyword. Inheritance uses class Child(Parent).
    Modules are imported with import statement. Packages organize modules.
    """
    
    print("\n\n📄 Testing with Python Document Content:")
    print("-" * 40)
    
    python_questions = generate_fallback_questions(
        python_content, 
        num_questions=3, 
        difficulty="medium", 
        topic_focus="Python"
    )
    
    print(f"Generated {len(python_questions)} Python-specific questions:")
    for i, question in enumerate(python_questions, 1):
        print(f"\n{i}. {question.question}")
        print(f"   Topic: {question.topic}")
        print(f"   Difficulty: {question.difficulty}")
    
    # Test with Data Structures content
    ds_content = """
    Arrays are contiguous memory locations storing same data type elements.
    Linked lists consist of nodes with data and pointer to next node.
    Stacks follow LIFO (Last In First Out) principle with push and pop operations.
    Queues follow FIFO (First In First Out) with enqueue and dequeue operations.
    Trees are hierarchical structures with root, parent, child, and leaf nodes.
    Binary search trees maintain sorted order with left < root < right property.
    Hash tables use hash functions to map keys to array indices for fast lookup.
    """
    
    print("\n\n📄 Testing with Data Structures Document Content:")
    print("-" * 40)
    
    ds_questions = generate_fallback_questions(
        ds_content, 
        num_questions=3, 
        difficulty="hard", 
        topic_focus="data structures"
    )
    
    print(f"Generated {len(ds_questions)} Data Structures questions:")
    for i, question in enumerate(ds_questions, 1):
        print(f"\n{i}. {question.question}")
        print(f"   Topic: {question.topic}")
        print(f"   Difficulty: {question.difficulty}")
    
    print("\n" + "=" * 60)
    print("🎉 Document-specific generation test completed!")
    
    # Verify questions are different and relevant
    java_topics = [q.topic for q in java_questions]
    python_topics = [q.topic for q in python_questions]
    ds_topics = [q.topic for q in ds_questions]
    
    print(f"\n📊 Analysis:")
    print(f"Java questions topics: {set(java_topics)}")
    print(f"Python questions topics: {set(python_topics)}")
    print(f"Data Structures topics: {set(ds_topics)}")
    
    # Check if questions contain relevant keywords
    java_text = " ".join([q.question for q in java_questions]).lower()
    python_text = " ".join([q.question for q in python_questions]).lower()
    ds_text = " ".join([q.question for q in ds_questions]).lower()
    
    print(f"\n🔍 Content Relevance Check:")
    print(f"Java questions mention Java concepts: {'java' in java_text or 'class' in java_text or 'object' in java_text}")
    print(f"Python questions mention Python concepts: {'python' in python_text or 'list' in python_text or 'dict' in python_text}")
    print(f"DS questions mention DS concepts: {'array' in ds_text or 'tree' in ds_text or 'stack' in ds_text}")

if __name__ == "__main__":
    test_document_specific_generation()
