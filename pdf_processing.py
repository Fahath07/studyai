"""
PDF Processing Module for StudyMate
Handles PDF text extraction, cleaning, and chunking for RAG system
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract clean text from a PDF file using PyMuPDF.

    Args:
        pdf_file: Streamlit uploaded file object

    Returns:
        str: Extracted and cleaned text
    """
    try:
        # Reset file pointer to beginning
        pdf_file.seek(0)

        # Read PDF from uploaded file
        pdf_bytes = pdf_file.read()
        logger.info(f"Read {len(pdf_bytes)} bytes from {pdf_file.name}")

        if len(pdf_bytes) == 0:
            logger.error(f"No data read from {pdf_file.name}")
            return ""

        # Open PDF document
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        logger.info(f"Opened PDF with {pdf_document.page_count} pages")

        text_content = []

        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]

            # Try multiple extraction methods
            text = ""

            # Method 1: Standard text extraction
            text = page.get_text("text")

            # Method 2: If no text found, try dict extraction (better for complex layouts)
            if not text.strip():
                text_dict = page.get_text("dict")
                text = extract_text_from_dict(text_dict)

            # Method 3: If still no text, try blocks extraction
            if not text.strip():
                blocks = page.get_text("blocks")
                text = "\n".join([block[4] for block in blocks if len(block) > 4 and block[4].strip()])

            logger.info(f"Page {page_num + 1}: extracted {len(text)} characters")

            if text.strip():  # Only add non-empty pages
                # Clean the extracted text
                cleaned_text = clean_text(text)
                if cleaned_text:
                    text_content.append(cleaned_text)
                    logger.info(f"Page {page_num + 1}: {len(cleaned_text)} characters after cleaning")

        pdf_document.close()

        # Combine all pages
        full_text = "\n\n".join(text_content)
        logger.info(f"Successfully extracted {len(full_text)} characters total from {pdf_file.name}")

        if len(full_text.strip()) == 0:
            logger.warning(f"No text content extracted from {pdf_file.name}. This might be a scanned PDF or image-based PDF.")
            return "No text content could be extracted from this PDF. This might be a scanned document or image-based PDF that requires OCR processing."

        return full_text

    except Exception as e:
        logger.error(f"Error extracting text from {pdf_file.name}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return ""


def extract_text_from_dict(text_dict: dict) -> str:
    """
    Extract text from PyMuPDF text dictionary format.

    Args:
        text_dict: Dictionary from page.get_text("dict")

    Returns:
        str: Extracted text
    """
    text_parts = []

    try:
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                    if line_text.strip():
                        text_parts.append(line_text.strip())
    except Exception as e:
        logger.error(f"Error extracting text from dict: {str(e)}")

    return "\n".join(text_parts)


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text by removing headers, footers, and formatting artifacts.
    
    Args:
        text: Raw text from PDF
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove common header/footer patterns
    # Page numbers at start/end of lines
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*Page\s+\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove URLs and email addresses (often in headers/footers)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[•·▪▫◦‣⁃]{2,}', '• ', text)
    text = re.sub(r'-{3,}', '---', text)
    text = re.sub(r'={3,}', '===', text)
    
    # Clean up spacing
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks for better context retention.
    
    Args:
        text: Input text to chunk
        chunk_size: Target number of words per chunk
        overlap: Number of words to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    if not text:
        return []
    
    # Split into words
    words = text.split()
    
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        # Calculate end position
        end = min(start + chunk_size, len(words))
        
        # Extract chunk
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        
        # Only add non-empty chunks
        if chunk_text.strip():
            chunks.append(chunk_text.strip())
        
        # Move start position (with overlap)
        if end >= len(words):
            break
        start = end - overlap
        
        # Ensure we don't get stuck in infinite loop
        if start <= 0:
            start = end
    
    logger.info(f"Created {len(chunks)} chunks from {len(words)} words")
    return chunks


def process_uploaded_pdfs(uploaded_files) -> List[Dict[str, Any]]:
    """
    Process multiple uploaded PDF files and return structured chunks.

    Args:
        uploaded_files: List of Streamlit uploaded file objects

    Returns:
        List[Dict]: List of chunk dictionaries with metadata
    """
    all_chunks = []
    processing_results = []

    for file_idx, uploaded_file in enumerate(uploaded_files):
        logger.info(f"Processing file {file_idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")

        # Validate file
        if not uploaded_file.name.lower().endswith('.pdf'):
            logger.warning(f"Skipping non-PDF file: {uploaded_file.name}")
            processing_results.append({
                "filename": uploaded_file.name,
                "status": "skipped",
                "reason": "Not a PDF file"
            })
            continue

        # Check file size
        file_size = uploaded_file.size if hasattr(uploaded_file, 'size') else len(uploaded_file.getvalue())
        logger.info(f"File size: {file_size} bytes")

        if file_size == 0:
            logger.warning(f"Empty file: {uploaded_file.name}")
            processing_results.append({
                "filename": uploaded_file.name,
                "status": "failed",
                "reason": "Empty file"
            })
            continue

        # Extract text from PDF
        text = extract_text_from_pdf(uploaded_file)

        if not text or len(text.strip()) == 0:
            logger.warning(f"No text extracted from {uploaded_file.name}")
            processing_results.append({
                "filename": uploaded_file.name,
                "status": "failed",
                "reason": "No text content found"
            })
            continue

        logger.info(f"Extracted {len(text)} characters from {uploaded_file.name}")

        # Create chunks
        chunks = chunk_text(text)

        if not chunks:
            logger.warning(f"No chunks created from {uploaded_file.name}")
            processing_results.append({
                "filename": uploaded_file.name,
                "status": "failed",
                "reason": "Could not create text chunks"
            })
            continue

        # Add metadata to each chunk
        file_chunks = 0
        for chunk_idx, chunk in enumerate(chunks):
            chunk_data = {
                "filename": uploaded_file.name,
                "chunk_index": chunk_idx,
                "text": chunk,
                "file_index": file_idx,
                "original_text_length": len(text)
            }
            all_chunks.append(chunk_data)
            file_chunks += 1

        processing_results.append({
            "filename": uploaded_file.name,
            "status": "success",
            "chunks_created": file_chunks,
            "text_length": len(text)
        })

        logger.info(f"Successfully processed {uploaded_file.name}: {file_chunks} chunks created")

    logger.info(f"Total chunks created: {len(all_chunks)} from {len(uploaded_files)} files")

    # Log processing summary
    successful_files = [r for r in processing_results if r["status"] == "success"]
    failed_files = [r for r in processing_results if r["status"] == "failed"]

    logger.info(f"Processing summary: {len(successful_files)} successful, {len(failed_files)} failed")

    if failed_files:
        for failed in failed_files:
            logger.warning(f"Failed to process {failed['filename']}: {failed['reason']}")

    return all_chunks


def get_processing_stats(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate statistics about processed chunks.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Dict: Processing statistics
    """
    if not chunks:
        return {"total_chunks": 0, "total_files": 0, "avg_chunk_length": 0}
    
    total_chunks = len(chunks)
    unique_files = len(set(chunk["filename"] for chunk in chunks))
    total_chars = sum(len(chunk["text"]) for chunk in chunks)
    avg_chunk_length = total_chars / total_chunks if total_chunks > 0 else 0
    
    file_stats = {}
    for chunk in chunks:
        filename = chunk["filename"]
        if filename not in file_stats:
            file_stats[filename] = 0
        file_stats[filename] += 1
    
    return {
        "total_chunks": total_chunks,
        "total_files": unique_files,
        "avg_chunk_length": round(avg_chunk_length, 2),
        "total_characters": total_chars,
        "file_breakdown": file_stats
    }
