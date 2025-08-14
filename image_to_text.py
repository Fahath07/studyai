#!/usr/bin/env python3
"""
Image to Text Module - Convert images to text using Hugging Face API
"""

import os
import io
import base64
import logging
import requests
from typing import Optional, Dict, Any
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# Try to import OCR libraries
try:
    import pytesseract
    import cv2
    import numpy as np

    # Configure Tesseract path for Windows
    if os.name == 'nt':  # Windows
        # Common Tesseract installation paths on Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

    LOCAL_OCR_AVAILABLE = True
except ImportError:
    LOCAL_OCR_AVAILABLE = False

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageToTextProcessor:
    """Handles image to text conversion using Hugging Face API."""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the ImageToTextProcessor.
        
        Args:
            api_token: Hugging Face API token
        """
        self.api_token = api_token or os.getenv('HUGGINGFACE_API_TOKEN')
        # Use OCR model for text extraction from images
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/trocr-base-printed"
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}

        # Fallback OCR models to try if the first one fails
        self.fallback_models = [
            "microsoft/trocr-large-printed",
            "microsoft/trocr-base-handwritten",
            "nlpconnect/vit-gpt2-image-captioning"  # Last resort for image description
        ]
        
    def is_available(self) -> bool:
        """Check if the image-to-text service is available."""
        return bool(self.api_token)
    
    def process_image(self, image_data: bytes) -> Optional[str]:
        """
        Convert image to text using Hugging Face OCR API with fallback models.

        Args:
            image_data: Raw image data in bytes

        Returns:
            Extracted text or None if failed
        """
        if not self.is_available():
            logger.error("Hugging Face API token not available")
            return None

        # Try primary OCR model first
        result = self._try_model(self.api_url, image_data)
        if result:
            return result

        # Try fallback models
        for model_name in self.fallback_models:
            fallback_url = f"https://api-inference.huggingface.co/models/{model_name}"
            logger.info(f"Trying fallback model: {model_name}")
            result = self._try_model(fallback_url, image_data)
            if result:
                return result

        # Try local OCR as last resort
        if LOCAL_OCR_AVAILABLE:
            logger.info("Trying local OCR with Tesseract")
            result = self._try_local_ocr(image_data)
            if result:
                return result

        logger.error("All OCR methods failed to extract text")
        return None

    def _try_model(self, api_url: str, image_data: bytes) -> Optional[str]:
        """
        Try a specific model for text extraction.

        Args:
            api_url: API endpoint URL
            image_data: Raw image data in bytes

        Returns:
            Extracted text or None if failed
        """
        try:
            # Make API request
            response = requests.post(
                api_url,
                headers=self.headers,
                data=image_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    # OCR models typically return generated_text
                    text = result[0].get('generated_text', '')
                    if text and len(text.strip()) > 0:
                        logger.info(f"Successfully extracted text: {len(text)} characters")
                        return text.strip()
                elif isinstance(result, dict):
                    # Some models might return different format
                    text = result.get('generated_text', result.get('text', ''))
                    if text and len(text.strip()) > 0:
                        logger.info(f"Successfully extracted text: {len(text)} characters")
                        return text.strip()

                logger.warning(f"No text found in API response: {result}")
                return None
            elif response.status_code == 503:
                logger.warning("Model is loading, this might take a few minutes")
                return None
            else:
                logger.warning(f"API request failed with status {response.status_code}: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.warning("API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error during model processing: {e}")
            return None

    def _try_local_ocr(self, image_data: bytes) -> Optional[str]:
        """
        Try local OCR using Tesseract as fallback.

        Args:
            image_data: Raw image data in bytes

        Returns:
            Extracted text or None if failed
        """
        if not LOCAL_OCR_AVAILABLE:
            return None

        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert PIL Image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocess image for better OCR
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)

            # Apply threshold to get better contrast
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Use Tesseract to extract text
            text = pytesseract.image_to_string(thresh, config='--psm 6')

            if text and len(text.strip()) > 0:
                logger.info(f"Local OCR extracted text: {len(text)} characters")
                return text.strip()
            else:
                logger.warning("Local OCR found no text")
                return None

        except Exception as e:
            logger.warning(f"Local OCR failed: {e}")
            return None
    
    def process_image_file(self, uploaded_file) -> Optional[str]:
        """
        Process an uploaded image file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Extracted text or None if failed
        """
        try:
            # Read the image data
            image_data = uploaded_file.getvalue()
            
            # Validate image format
            try:
                image = Image.open(io.BytesIO(image_data))
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Convert back to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                image_data = img_byte_arr.getvalue()
                
            except Exception as e:
                logger.error(f"Error processing image format: {e}")
                return None
            
            # Process the image
            return self.process_image(image_data)
            
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}")
            return None

def get_image_processor() -> ImageToTextProcessor:
    """Get a configured ImageToTextProcessor instance."""
    return ImageToTextProcessor()

def handle_image_upload():
    """Handle image upload and text extraction in Streamlit interface."""
    st.subheader("🖼️ Image to Text Conversion")
    st.markdown("*Extract text from images using OCR (Optical Character Recognition)*")

    # Check if API is available
    processor = get_image_processor()

    # Show available OCR methods
    col1, col2 = st.columns(2)

    with col1:
        if processor.is_available():
            st.success("✅ Hugging Face OCR API ready")
        else:
            st.warning("⚠️ Hugging Face API not configured")

    with col2:
        if LOCAL_OCR_AVAILABLE:
            st.success("✅ Local OCR (Tesseract) available")
        else:
            st.info("💡 Install pytesseract & opencv for local OCR")

    # Show instructions
    if not processor.is_available() and not LOCAL_OCR_AVAILABLE:
        st.error("❌ No OCR methods available. Please configure at least one:")
        st.info("**Option 1:** Get free Hugging Face API token from: https://huggingface.co/settings/tokens")
        st.info("**Option 2:** Install local OCR: `pip install pytesseract opencv-python`")
        return

    st.divider()
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose image files",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
        accept_multiple_files=True,
        help="Upload images to extract text content"
    )
    
    if uploaded_files:
        st.write(f"📁 **{len(uploaded_files)} image(s) selected:**")
        
        for i, uploaded_file in enumerate(uploaded_files):
            file_size = len(uploaded_file.getvalue()) if hasattr(uploaded_file, 'getvalue') else 0
            st.write(f"   {i+1}. {uploaded_file.name} ({file_size:,} bytes)")
        
        if st.button("🔍 Extract Text from Images", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_extracted_text = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Display the image
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(uploaded_file, caption=uploaded_file.name, width=200)
                
                with col2:
                    with st.spinner(f"Extracting text from {uploaded_file.name}..."):
                        extracted_text = processor.process_image_file(uploaded_file)
                        
                        if extracted_text:
                            st.success(f"✅ Text extracted successfully!")

                            # Show extracted text with character count
                            st.markdown(f"**Extracted {len(extracted_text)} characters:**")
                            st.text_area(
                                f"Text from {uploaded_file.name}:",
                                value=extracted_text,
                                height=100,
                                key=f"extracted_text_{i}"
                            )
                            all_extracted_text.append({
                                'filename': uploaded_file.name,
                                'text': extracted_text
                            })
                        else:
                            st.error(f"❌ Failed to extract text from {uploaded_file.name}")
                            st.info("💡 **Tips for better OCR results:**")
                            st.write("• Ensure the image has good contrast")
                            st.write("• Make sure text is clearly visible")
                            st.write("• Try images with printed text rather than handwritten")
                            st.write("• Higher resolution images work better")
                
                st.divider()
            
            # Summary
            if all_extracted_text:
                st.success(f"🎉 Successfully processed {len(all_extracted_text)} out of {len(uploaded_files)} images")
                
                # Option to combine all text
                if len(all_extracted_text) > 1:
                    if st.button("📝 Combine All Extracted Text"):
                        combined_text = "\n\n".join([
                            f"=== {item['filename']} ===\n{item['text']}"
                            for item in all_extracted_text
                        ])
                        
                        st.text_area(
                            "Combined extracted text:",
                            value=combined_text,
                            height=300,
                            key="combined_text"
                        )
                        
                        # Option to save as chunks for Q&A
                        if st.button("💾 Save to Document Database"):
                            # Convert to chunks and add to session state
                            from pdf_processing import create_text_chunks
                            
                            chunks = create_text_chunks(combined_text, source="Image Extraction")
                            
                            if not hasattr(st.session_state, 'chunks'):
                                st.session_state.chunks = []
                            if not hasattr(st.session_state, 'processed_files'):
                                st.session_state.processed_files = []
                            
                            # Add to existing chunks
                            st.session_state.chunks.extend(chunks)
                            st.session_state.processed_files.extend([f"📷 {item['filename']}" for item in all_extracted_text])
                            
                            # Re-initialize retrieval system
                            from embedding_retrieval import initialize_retrieval_system
                            st.session_state.retriever = initialize_retrieval_system(st.session_state.chunks)
                            
                            st.success(f"✅ Added {len(chunks)} text chunks to document database!")
                            st.info("💡 You can now ask questions about the extracted text in Q&A mode.")
            
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete!")

def display_api_info():
    """Display information about getting Hugging Face API key."""
    st.info("""
    ### 🔑 How to get your Hugging Face API Token:
    
    1. **Visit**: https://huggingface.co/settings/tokens
    2. **Sign up/Login** to your Hugging Face account
    3. **Create a new token** with "Read" permissions
    4. **Copy the token** and add it to your `.env` file as `HUGGINGFACE_API_TOKEN`
    5. **Restart the application** to apply the changes
    
    The token is **free** and allows you to use Hugging Face's image-to-text models!
    """)
