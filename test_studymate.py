"""
Test Script for StudyMate Components
Basic validation of core functionality
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test if all modules can be imported successfully."""
    print("Testing module imports...")
    
    try:
        import pdf_processing
        print("✅ pdf_processing imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pdf_processing: {e}")
        return False
    
    try:
        import embedding_retrieval
        print("✅ embedding_retrieval imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import embedding_retrieval: {e}")
        return False
    
    try:
        import watsonx_integration
        print("✅ watsonx_integration imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import watsonx_integration: {e}")
        return False
    
    try:
        import utils
        print("✅ utils imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import utils: {e}")
        return False
    
    return True


def test_environment():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    
    from utils import load_environment_variables
    
    config_status = load_environment_variables()
    
    if config_status["all_configured"]:
        print("✅ All environment variables configured")
        return True
    else:
        print("⚠️ Some environment variables missing:")
        for var, status in config_status.items():
            if var != "all_configured" and not status["configured"]:
                print(f"   - {var}: Not configured")
        print("   Please update your .env file with IBM Watsonx credentials")
        return False


def test_text_processing():
    """Test basic text processing functions."""
    print("\nTesting text processing...")
    
    from pdf_processing import clean_text, chunk_text
    from utils import validate_question, truncate_text
    
    # Test text cleaning
    sample_text = "This is a test   text\n\n\nwith multiple   spaces."
    cleaned = clean_text(sample_text)
    print(f"✅ Text cleaning: '{sample_text}' -> '{cleaned}'")
    
    # Test chunking
    long_text = " ".join(["word"] * 1000)  # 1000 words
    chunks = chunk_text(long_text, chunk_size=100, overlap=20)
    print(f"✅ Text chunking: {len(long_text.split())} words -> {len(chunks)} chunks")
    
    # Test question validation
    valid_question = "What is machine learning?"
    validation = validate_question(valid_question)
    print(f"✅ Question validation: '{valid_question}' -> {validation['valid']}")
    
    # Test text truncation
    long_text = "This is a very long text that should be truncated"
    truncated = truncate_text(long_text, max_length=20)
    print(f"✅ Text truncation: '{long_text}' -> '{truncated}'")
    
    return True


def test_embedding_system():
    """Test embedding system initialization."""
    print("\nTesting embedding system...")
    
    try:
        from embedding_retrieval import EmbeddingRetriever
        
        # Create sample chunks
        sample_chunks = [
            {"filename": "test.pdf", "chunk_index": 0, "text": "This is about machine learning algorithms."},
            {"filename": "test.pdf", "chunk_index": 1, "text": "Deep learning is a subset of machine learning."},
            {"filename": "test.pdf", "chunk_index": 2, "text": "Neural networks are used in deep learning."}
        ]
        
        # Initialize retriever
        retriever = EmbeddingRetriever()
        print("✅ EmbeddingRetriever initialized")
        
        # Create embeddings
        embeddings = retriever.create_embeddings(sample_chunks)
        print(f"✅ Embeddings created: shape {embeddings.shape}")
        
        # Build index
        retriever.build_faiss_index(embeddings)
        print("✅ FAISS index built")
        
        # Test retrieval
        results = retriever.retrieve_relevant_chunks("What is machine learning?", top_k=2)
        print(f"✅ Retrieval test: found {len(results)} relevant chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding system test failed: {e}")
        return False


def test_session_management():
    """Test session management utilities."""
    print("\nTesting session management...")
    
    from utils import create_qa_session_export, get_session_stats, format_qa_for_display
    
    # Sample Q&A history
    sample_qa = [
        {
            "question": "What is AI?",
            "answer": "Artificial Intelligence is...",
            "sources": [{"filename": "ai_book.pdf", "section": "Chapter 1"}],
            "timestamp": datetime.now()
        }
    ]
    
    # Test export
    export_text = create_qa_session_export(sample_qa)
    print(f"✅ Session export: {len(export_text)} characters generated")
    
    # Test stats
    stats = get_session_stats(sample_qa)
    print(f"✅ Session stats: {stats['total_questions']} questions")
    
    # Test formatting
    formatted = format_qa_for_display(sample_qa[0])
    print(f"✅ Q&A formatting: question length {len(formatted['question'])}")
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("StudyMate Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_text_processing,
        test_embedding_system,
        test_session_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! StudyMate is ready to use.")
        print("\nTo run the application:")
        print("streamlit run streamlit_app.py")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
