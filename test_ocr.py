#!/usr/bin/env python3
"""
Test script for OCR functionality
"""

import os
from image_to_text import ImageToTextProcessor

def test_ocr():
    """Test OCR functionality."""
    print("Testing OCR functionality...")
    
    processor = ImageToTextProcessor()
    
    # Check if Hugging Face API is available
    if processor.is_available():
        print("✅ Hugging Face API available")
    else:
        print("❌ Hugging Face API not available")
    
    # Check if local OCR is available
    try:
        import pytesseract
        import cv2
        import numpy as np
        print("✅ Local OCR libraries available")
        
        # Test Tesseract installation
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version: {version}")
        except Exception as e:
            print(f"❌ Tesseract not properly configured: {e}")
            
    except ImportError as e:
        print(f"❌ Local OCR libraries not available: {e}")

if __name__ == "__main__":
    test_ocr()
