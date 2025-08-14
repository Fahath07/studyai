#!/usr/bin/env python3
"""
Complete Export Functionality Test - Fixed Version
Tests both Q&A and Quiz export features
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List

def test_qa_export():
    """Test Q&A session export functionality."""
    print("🧪 Testing Q&A Export Functionality")
    print("=" * 50)
    
    try:
        from utils import create_qa_session_export, create_qa_session_pdf_export
        
        # Create sample Q&A data
        qa_history = [
            {
                "question": "What is artificial intelligence?",
                "answer": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can perform tasks that typically require human intelligence, such as learning, reasoning, problem-solving, and decision-making.",
                "timestamp": datetime.now(),
                "sources": [
                    {"filename": "ai_textbook.pdf", "section": "Chapter 1: Introduction"},
                    {"filename": "ml_guide.pdf", "section": "Section 2.1: AI Fundamentals"}
                ]
            },
            {
                "question": "Explain machine learning",
                "answer": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make predictions or decisions.",
                "timestamp": datetime.now(),
                "sources": [
                    {"filename": "ml_guide.pdf", "section": "Chapter 3: ML Basics"}
                ]
            },
            {
                "question": "What are neural networks?",
                "answer": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information and can learn complex patterns in data through training.",
                "timestamp": datetime.now(),
                "sources": []
            }
        ]
        
        session_info = {
            "files_processed": ["ai_textbook.pdf", "ml_guide.pdf"]
        }
        
        # Test text export
        print("📝 Testing text export...")
        text_export = create_qa_session_export(qa_history, session_info)
        
        if text_export and len(text_export) > 100:
            print("✅ Text export successful")
            print(f"   Length: {len(text_export)} characters")
            
            # Save to file
            with open("test_qa_session_fixed.txt", "w", encoding="utf-8") as f:
                f.write(text_export)
            print("💾 Saved as: test_qa_session_fixed.txt")
        else:
            print("❌ Text export failed")
            return False
        
        # Test PDF export
        print("📑 Testing PDF export...")
        pdf_buffer = create_qa_session_pdf_export(qa_history, session_info)
        
        if pdf_buffer:
            print("✅ PDF export successful")
            print(f"   Size: {len(pdf_buffer.getvalue())} bytes")
            
            # Save to file
            with open("test_qa_session_fixed.pdf", "wb") as f:
                f.write(pdf_buffer.getvalue())
            print("💾 Saved as: test_qa_session_fixed.pdf")
        else:
            print("❌ PDF export failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Q&A export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quiz_export():
    """Test quiz export functionality."""
    print("\n🧠 Testing Quiz Export Functionality")
    print("=" * 50)
    
    try:
        from quiz_generator import MCQuestion, QuizSession, MCQOption
        from quiz_export import prepare_quiz_export_data, create_quiz_word_document, create_quiz_pdf_document
        
        # Create sample quiz data
        questions = [
            MCQuestion(
                question="What does AI stand for?",
                options=[
                    MCQOption("Artificial Intelligence", True),
                    MCQOption("Automated Intelligence", False),
                    MCQOption("Advanced Intelligence", False),
                    MCQOption("Applied Intelligence", False)
                ],
                difficulty="medium",
                topic="Artificial Intelligence",
                explanation="AI stands for Artificial Intelligence, which refers to the simulation of human intelligence in machines.",
                source_context="AI fundamentals from textbook"
            ),
            MCQuestion(
                question="Which of the following is a type of machine learning?",
                options=[
                    MCQOption("Supervised Learning", False),
                    MCQOption("Unsupervised Learning", False),
                    MCQOption("Reinforcement Learning", False),
                    MCQOption("All of the above", True)
                ],
                difficulty="medium",
                topic="Machine Learning",
                explanation="All three - supervised, unsupervised, and reinforcement learning - are major types of machine learning.",
                source_context="ML types from course material"
            ),
            MCQuestion(
                question="What is a neural network?",
                options=[
                    MCQOption("A computer network", False),
                    MCQOption("A biological system", False),
                    MCQOption("A computing model inspired by the brain", True),
                    MCQOption("A type of database", False)
                ],
                difficulty="medium",
                topic="Neural Networks",
                explanation="Neural networks are computing models inspired by the structure and function of biological neural networks in the brain.",
                source_context="Neural network definition from AI textbook"
            )
        ]
        
        # Create quiz session with correct parameters
        quiz_session = QuizSession(
            session_id="test_session_123",
            questions=questions,
            user_answers={0: 0, 1: 3, 2: 2},  # All correct answers
            start_time=datetime.now(),
            end_time=datetime.now(),
            score=3,
            total_questions=3
        )
        
        # Create a dictionary representation for export (matching what the app uses)
        quiz_session_dict = {
            "session_id": quiz_session.session_id,
            "questions": quiz_session.questions,
            "user_answers": quiz_session.user_answers,
            "start_time": quiz_session.start_time,
            "end_time": quiz_session.end_time,
            "score": quiz_session.score,
            "total_questions": quiz_session.total_questions,
            "difficulty": "medium",
            "topic_focus": "Artificial Intelligence",
            "generation_method": "AI-generated",
            "source_documents": ["ai_textbook.pdf", "ml_guide.pdf"]
        }
        
        print("📊 Testing quiz data preparation...")
        
        # Test with answers
        quiz_data_with_answers = prepare_quiz_export_data(quiz_session_dict, include_answers=True)
        if quiz_data_with_answers:
            print("✅ Quiz data preparation (with answers) successful")
            print(f"   Title: {quiz_data_with_answers.get('title', 'N/A')}")
            print(f"   Questions: {len(quiz_data_with_answers.get('questions', []))}")
        else:
            print("❌ Quiz data preparation (with answers) failed")
            return False
        
        # Test without answers
        quiz_data_no_answers = prepare_quiz_export_data(quiz_session_dict, include_answers=False)
        if quiz_data_no_answers:
            print("✅ Quiz data preparation (questions only) successful")
        else:
            print("❌ Quiz data preparation (questions only) failed")
            return False
        
        # Test Word export
        print("📄 Testing Word document export...")
        
        # With answers
        word_buffer_with_answers = create_quiz_word_document(quiz_data_with_answers)
        if word_buffer_with_answers:
            print("✅ Word export (with answers) successful")
            with open("test_quiz_with_answers_fixed.docx", "wb") as f:
                f.write(word_buffer_with_answers.getvalue())
            print("💾 Saved as: test_quiz_with_answers_fixed.docx")
        else:
            print("❌ Word export (with answers) failed")
            return False
        
        # Questions only
        word_buffer_no_answers = create_quiz_word_document(quiz_data_no_answers)
        if word_buffer_no_answers:
            print("✅ Word export (questions only) successful")
            with open("test_quiz_questions_only_fixed.docx", "wb") as f:
                f.write(word_buffer_no_answers.getvalue())
            print("💾 Saved as: test_quiz_questions_only_fixed.docx")
        else:
            print("❌ Word export (questions only) failed")
            return False
        
        # Test PDF export
        print("📑 Testing PDF document export...")
        
        # With answers
        pdf_buffer_with_answers = create_quiz_pdf_document(quiz_data_with_answers)
        if pdf_buffer_with_answers:
            print("✅ PDF export (with answers) successful")
            with open("test_quiz_with_answers_fixed.pdf", "wb") as f:
                f.write(pdf_buffer_with_answers.getvalue())
            print("💾 Saved as: test_quiz_with_answers_fixed.pdf")
        else:
            print("❌ PDF export (with answers) failed")
            return False
        
        # Questions only
        pdf_buffer_no_answers = create_quiz_pdf_document(quiz_data_no_answers)
        if pdf_buffer_no_answers:
            print("✅ PDF export (questions only) successful")
            with open("test_quiz_questions_only_fixed.pdf", "wb") as f:
                f.write(pdf_buffer_no_answers.getvalue())
            print("💾 Saved as: test_quiz_questions_only_fixed.pdf")
        else:
            print("❌ PDF export (questions only) failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Quiz export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run complete export functionality tests."""
    print("🚀 StudyMate Export Functionality Test Suite - Fixed Version")
    print("=" * 70)
    
    # Test Q&A export
    qa_success = test_qa_export()
    
    # Test Quiz export
    quiz_success = test_quiz_export()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    if qa_success:
        print("✅ Q&A Export: PASSED")
    else:
        print("❌ Q&A Export: FAILED")
    
    if quiz_success:
        print("✅ Quiz Export: PASSED")
    else:
        print("❌ Quiz Export: FAILED")
    
    if qa_success and quiz_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("📄 Export functionality is working correctly for both Q&A and Quiz modes.")
        print("\nGenerated test files:")
        print("📝 test_qa_session_fixed.txt")
        print("📑 test_qa_session_fixed.pdf")
        print("📄 test_quiz_with_answers_fixed.docx")
        print("📄 test_quiz_questions_only_fixed.docx")
        print("📑 test_quiz_with_answers_fixed.pdf")
        print("📑 test_quiz_questions_only_fixed.pdf")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the error messages above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)