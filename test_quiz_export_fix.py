#!/usr/bin/env python3
"""
Test script to verify the quiz export fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz_generator import QuizSession, MCQuestion, MCQOption, create_quiz_session
from quiz_export import prepare_quiz_export_data, create_quiz_word_document, create_quiz_pdf_document
from datetime import datetime

def test_quiz_export_fix():
    """Test that quiz export works with QuizSession objects."""
    print("🧪 Testing Quiz Export Fix")
    print("=" * 50)
    
    # Create sample questions
    questions = []
    
    # Question 1
    options1 = [
        MCQOption("Option A", False),
        MCQOption("Option B", True),
        MCQOption("Option C", False),
        MCQOption("Option D", False)
    ]
    question1 = MCQuestion(
        question="What is the correct answer?",
        options=options1,
        difficulty="medium",
        topic="Programming",
        explanation="Option B is correct because...",
        source_context="Sample context"
    )
    questions.append(question1)
    
    # Question 2
    options2 = [
        MCQOption("True", True),
        MCQOption("False", False),
        MCQOption("Maybe", False),
        MCQOption("Unknown", False)
    ]
    question2 = MCQuestion(
        question="Is this a test question?",
        options=options2,
        difficulty="easy",
        topic="General",
        explanation="True is correct because this is indeed a test.",
        source_context="Sample context"
    )
    questions.append(question2)
    
    # Create quiz session
    print("📝 Creating quiz session...")
    quiz_session = create_quiz_session(questions)
    print(f"✅ Quiz session created with {len(quiz_session.questions)} questions")
    
    # Test prepare_quiz_export_data
    print("\n📊 Testing prepare_quiz_export_data...")
    try:
        quiz_data = prepare_quiz_export_data(quiz_session, include_answers=True)
        print(f"✅ Quiz data prepared successfully")
        print(f"   Title: {quiz_data.title}")
        print(f"   Questions: {len(quiz_data.questions)}")
        print(f"   Difficulty: {quiz_data.metadata['difficulty']}")
        print(f"   Topic: {quiz_data.metadata['topic_focus']}")
    except Exception as e:
        print(f"❌ Error preparing quiz data: {e}")
        return False
    
    # Test Word document generation
    print("\n📄 Testing Word document generation...")
    try:
        word_buffer = create_quiz_word_document(quiz_data)
        if word_buffer:
            print("✅ Word document generated successfully")
            with open("test_export_fix.docx", "wb") as f:
                f.write(word_buffer.getvalue())
            print("💾 Saved as: test_export_fix.docx")
        else:
            print("❌ Word document generation returned None")
            return False
    except Exception as e:
        print(f"❌ Error generating Word document: {e}")
        return False
    
    # Test PDF document generation
    print("\n📑 Testing PDF document generation...")
    try:
        pdf_buffer = create_quiz_pdf_document(quiz_data)
        if pdf_buffer:
            print("✅ PDF document generated successfully")
            with open("test_export_fix.pdf", "wb") as f:
                f.write(pdf_buffer.getvalue())
            print("💾 Saved as: test_export_fix.pdf")
        else:
            print("❌ PDF document generation returned None")
            return False
    except Exception as e:
        print(f"❌ Error generating PDF document: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Quiz export fix test completed successfully!")
    print("\nGenerated files:")
    print("📄 test_export_fix.docx")
    print("📑 test_export_fix.pdf")
    
    return True

if __name__ == "__main__":
    success = test_quiz_export_fix()
    if success:
        print("\n✅ All tests passed! Quiz export is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
