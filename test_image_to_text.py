#!/usr/bin/env python3
"""
Test script for Image to Text functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from image_to_text import ImageToTextProcessor, get_image_processor
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Create a simple test image with text."""
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add some text
    text = "Hello World!\nThis is a test image\nfor OCR processing."
    draw.text((50, 50), text, fill='black', font=font)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_image_processor():
    """Test the ImageToTextProcessor functionality."""
    print("🧪 Testing Image to Text Functionality")
    print("=" * 60)
    
    # Initialize processor
    processor = get_image_processor()
    
    # Check availability
    print(f"📋 API Token Available: {processor.is_available()}")
    
    if not processor.is_available():
        print("❌ Hugging Face API token not configured")
        print("💡 Please add your token to the .env file as HUGGINGFACE_API_TOKEN")
        print("🔗 Get your token from: https://huggingface.co/settings/tokens")
        return False
    
    print("✅ Hugging Face API token configured")
    
    # Create test image
    print("\n📸 Creating test image...")
    test_image_data = create_test_image()
    print(f"✅ Test image created ({len(test_image_data)} bytes)")
    
    # Process the image
    print("\n🔍 Processing image with Hugging Face API...")
    try:
        extracted_text = processor.process_image(test_image_data)
        
        if extracted_text:
            print("✅ Text extraction successful!")
            print(f"📝 Extracted text: '{extracted_text}'")
            print(f"📊 Text length: {len(extracted_text)} characters")
        else:
            print("❌ Text extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Image to Text test completed successfully!")
    return True

def display_setup_instructions():
    """Display setup instructions for Hugging Face API."""
    print("\n" + "=" * 60)
    print("🔑 HUGGING FACE API SETUP INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. 🌐 Visit: https://huggingface.co/settings/tokens")
    print("2. 📝 Sign up or log in to your Hugging Face account")
    print("3. ➕ Click 'New token' to create a new API token")
    print("4. 📋 Choose 'Read' permissions (free tier)")
    print("5. 📄 Copy the generated token")
    print("6. 📁 Open your .env file in the project directory")
    print("7. ✏️  Add or update the line:")
    print("   HUGGINGFACE_API_TOKEN=your_token_here")
    print("8. 🔄 Restart the application")
    print()
    print("💡 The Hugging Face API is FREE for basic usage!")
    print("🎯 This enables image-to-text conversion using BLIP model")
    print("📊 Rate limits: ~1000 requests per month on free tier")
    print()
    print("🔗 Direct link: https://huggingface.co/settings/tokens")
    print("=" * 60)

if __name__ == "__main__":
    success = test_image_processor()
    
    if not success:
        display_setup_instructions()
    else:
        print("\n✅ Image to Text functionality is working correctly!")
        print("🚀 You can now use the Image to Text feature in the app!")
