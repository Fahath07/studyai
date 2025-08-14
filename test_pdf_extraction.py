"""
Test script to verify PDF text extraction functionality
"""

import fitz  # PyMuPDF
import io
from pdf_processing import extract_text_from_pdf, extract_text_from_dict

def create_test_pdf():
    """Create a simple test PDF with text content."""
    # Create a new PDF document
    doc = fitz.open()
    
    # Add a page
    page = doc.new_page()
    
    # Add some text
    text = """
    This is a test PDF document for StudyMate.
    
    Chapter 1: Introduction to Machine Learning
    
    Machine learning is a subset of artificial intelligence (AI) that provides systems 
    the ability to automatically learn and improve from experience without being 
    explicitly programmed.
    
    Key concepts include:
    • Supervised learning
    • Unsupervised learning  
    • Reinforcement learning
    
    This document contains multiple paragraphs to test the text extraction 
    functionality of the StudyMate application.
    """
    
    # Insert text into the page
    page.insert_text((50, 50), text, fontsize=12)
    
    # Save to bytes
    pdf_bytes = doc.tobytes()
    doc.close()
    
    return pdf_bytes

def test_pdf_extraction():
    """Test PDF text extraction with a sample PDF."""
    print("Creating test PDF...")
    pdf_bytes = create_test_pdf()
    
    # Create a file-like object
    class MockUploadedFile:
        def __init__(self, content, name):
            self.content = content
            self.name = name
            self.position = 0
        
        def read(self):
            return self.content
        
        def seek(self, position):
            self.position = position
        
        def getvalue(self):
            return self.content
    
    # Test extraction
    mock_file = MockUploadedFile(pdf_bytes, "test.pdf")
    
    print("Testing text extraction...")
    extracted_text = extract_text_from_pdf(mock_file)
    
    print(f"Extracted text length: {len(extracted_text)}")
    print("Extracted text preview:")
    print("-" * 50)
    print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
    print("-" * 50)
    
    if extracted_text and len(extracted_text.strip()) > 0:
        print("✅ PDF text extraction is working!")
        return True
    else:
        print("❌ PDF text extraction failed!")
        return False

def test_different_extraction_methods():
    """Test different PyMuPDF extraction methods."""
    print("\nTesting different extraction methods...")
    pdf_bytes = create_test_pdf()
    
    # Open the PDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    
    # Method 1: get_text("text")
    text1 = page.get_text("text")
    print(f"Method 1 (text): {len(text1)} characters")
    
    # Method 2: get_text("dict")
    text_dict = page.get_text("dict")
    text2 = extract_text_from_dict(text_dict)
    print(f"Method 2 (dict): {len(text2)} characters")
    
    # Method 3: get_text("blocks")
    blocks = page.get_text("blocks")
    text3 = "\n".join([block[4] for block in blocks if len(block) > 4 and block[4].strip()])
    print(f"Method 3 (blocks): {len(text3)} characters")
    
    doc.close()
    
    # Show which methods work
    methods_working = []
    if text1.strip(): methods_working.append("text")
    if text2.strip(): methods_working.append("dict")
    if text3.strip(): methods_working.append("blocks")
    
    print(f"Working methods: {methods_working}")
    
    return len(methods_working) > 0

if __name__ == "__main__":
    print("=" * 60)
    print("PDF Text Extraction Test")
    print("=" * 60)
    
    try:
        # Test basic extraction
        success1 = test_pdf_extraction()
        
        # Test different methods
        success2 = test_different_extraction_methods()
        
        print("\n" + "=" * 60)
        if success1 and success2:
            print("🎉 All PDF extraction tests passed!")
        else:
            print("⚠️ Some PDF extraction tests failed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        print(traceback.format_exc())
