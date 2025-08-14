#!/usr/bin/env python3
"""
Test script for quiz export functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz_export import create_quiz_word_document, create_quiz_pdf_document, QuizExportData

def test_document_generation():
    """Test Word and PDF document generation."""
    print("🧪 Testing Quiz Document Generation")
    print("=" * 60)
    
    # Sample quiz data
    sample_questions = [
        {
            'question': 'What is the primary purpose of a Java class?',
            'options': [
                {'text': 'To define a blueprint for objects', 'is_correct': True},
                {'text': 'To store data only', 'is_correct': False},
                {'text': 'To execute main method', 'is_correct': False},
                {'text': 'To handle exceptions', 'is_correct': False}
            ],
            'explanation': 'A Java class serves as a blueprint or template for creating objects, defining their structure and behavior.',
            'topic': 'Object-Oriented Programming',
            'difficulty': 'medium'
        },
        {
            'question': 'Which keyword is used to create an object in Java?',
            'options': [
                {'text': 'create', 'is_correct': False},
                {'text': 'new', 'is_correct': True},
                {'text': 'object', 'is_correct': False},
                {'text': 'instance', 'is_correct': False}
            ],
            'explanation': 'The "new" keyword is used in Java to create new instances (objects) of a class.',
            'topic': 'Java Syntax',
            'difficulty': 'easy'
        },
        {
            'question': 'What is the time complexity of searching in a balanced binary search tree?',
            'options': [
                {'text': 'O(1)', 'is_correct': False},
                {'text': 'O(log n)', 'is_correct': True},
                {'text': 'O(n)', 'is_correct': False},
                {'text': 'O(n²)', 'is_correct': False}
            ],
            'explanation': 'In a balanced binary search tree, the height is O(log n), making search operations O(log n) time complexity.',
            'topic': 'Data Structures',
            'difficulty': 'hard'
        }
    ]
    
    metadata = {
        'generated_time': '2025-01-13 15:30:00',
        'difficulty': 'mixed',
        'topic_focus': 'Java Programming',
        'total_questions': len(sample_questions)
    }
    
    # Test with answers
    print("\n📄 Testing Word Document Generation (with answers)...")
    quiz_data_with_answers = QuizExportData(
        title="Java Programming Quiz - Mixed Difficulty",
        questions=sample_questions,
        metadata=metadata,
        include_answers=True
    )
    
    word_buffer = create_quiz_word_document(quiz_data_with_answers)
    if word_buffer:
        print("✅ Word document with answers generated successfully")
        with open("test_quiz_with_answers.docx", "wb") as f:
            f.write(word_buffer.getvalue())
        print("💾 Saved as: test_quiz_with_answers.docx")
    else:
        print("❌ Failed to generate Word document with answers")
    
    # Test without answers
    print("\n📄 Testing Word Document Generation (questions only)...")
    quiz_data_questions_only = QuizExportData(
        title="Java Programming Quiz - Mixed Difficulty (Questions Only)",
        questions=sample_questions,
        metadata=metadata,
        include_answers=False
    )
    
    word_buffer = create_quiz_word_document(quiz_data_questions_only)
    if word_buffer:
        print("✅ Word document (questions only) generated successfully")
        with open("test_quiz_questions_only.docx", "wb") as f:
            f.write(word_buffer.getvalue())
        print("💾 Saved as: test_quiz_questions_only.docx")
    else:
        print("❌ Failed to generate Word document (questions only)")
    
    # Test PDF with answers
    print("\n📑 Testing PDF Document Generation (with answers)...")
    pdf_buffer = create_quiz_pdf_document(quiz_data_with_answers)
    if pdf_buffer:
        print("✅ PDF document with answers generated successfully")
        with open("test_quiz_with_answers.pdf", "wb") as f:
            f.write(pdf_buffer.getvalue())
        print("💾 Saved as: test_quiz_with_answers.pdf")
    else:
        print("❌ Failed to generate PDF document with answers")
    
    # Test PDF without answers
    print("\n📑 Testing PDF Document Generation (questions only)...")
    pdf_buffer = create_quiz_pdf_document(quiz_data_questions_only)
    if pdf_buffer:
        print("✅ PDF document (questions only) generated successfully")
        with open("test_quiz_questions_only.pdf", "wb") as f:
            f.write(pdf_buffer.getvalue())
        print("💾 Saved as: test_quiz_questions_only.pdf")
    else:
        print("❌ Failed to generate PDF document (questions only)")
    
    print("\n" + "=" * 60)
    print("🎉 Document generation test completed!")
    print("\nGenerated files:")
    print("📄 test_quiz_with_answers.docx")
    print("📄 test_quiz_questions_only.docx")
    print("📑 test_quiz_with_answers.pdf")
    print("📑 test_quiz_questions_only.pdf")

if __name__ == "__main__":
    test_document_generation()
