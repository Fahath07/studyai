"""
Utility Functions for StudyMate
Helper functions for session management, text processing, and export functionality
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_environment_variables():
    """
    Load and validate environment variables for the application.
    
    Returns:
        Dict: Environment configuration status
    """
    from dotenv import load_dotenv
    
    # Load .env file
    load_dotenv()
    
    required_vars = ["IBM_API_KEY", "IBM_PROJECT_ID", "IBM_URL"]
    config_status = {}
    
    for var in required_vars:
        value = os.getenv(var)
        config_status[var] = {
            "configured": bool(value),
            "value_preview": value[:10] + "..." if value and len(value) > 10 else value
        }
    
    all_configured = all(config_status[var]["configured"] for var in required_vars)
    config_status["all_configured"] = all_configured
    
    return config_status


def validate_question(question: str) -> Dict[str, Any]:
    """
    Validate user question input.
    
    Args:
        question: User's input question
        
    Returns:
        Dict: Validation result with status and message
    """
    result = {"valid": False, "message": "", "cleaned_question": ""}
    
    if not question or not question.strip():
        result["message"] = "Please enter a question."
        return result
    
    cleaned = question.strip()
    
    # Check minimum length
    if len(cleaned) < 3:
        result["message"] = "Question is too short. Please provide more detail."
        return result
    
    # Check maximum length
    if len(cleaned) > 1000:
        result["message"] = "Question is too long. Please keep it under 1000 characters."
        return result
    
    # Check for meaningful content (not just punctuation/numbers)
    if not re.search(r'[a-zA-Z]', cleaned):
        result["message"] = "Please enter a question with text content."
        return result
    
    result["valid"] = True
    result["cleaned_question"] = cleaned
    result["message"] = "Question is valid."
    
    return result


def format_qa_for_display(qa_item: Dict[str, Any]) -> Dict[str, str]:
    """
    Format Q&A item for display in the UI.
    
    Args:
        qa_item: Q&A dictionary with question, answer, timestamp, sources
        
    Returns:
        Dict: Formatted display data
    """
    timestamp = qa_item.get("timestamp", datetime.now())
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except:
            timestamp = datetime.now()
    
    formatted_time = timestamp.strftime("%H:%M:%S")
    
    question = qa_item.get("question", "No question")
    answer = qa_item.get("answer", "No answer")
    sources = qa_item.get("sources", [])
    
    # Truncate long answers for display
    display_answer = answer
    if len(answer) > 500:
        display_answer = answer[:500] + "..."
    
    return {
        "time": formatted_time,
        "question": question,
        "answer": display_answer,
        "full_answer": answer,
        "source_count": len(sources),
        "sources": sources
    }


def create_qa_session_export(qa_history: List[Dict[str, Any]],
                           session_info: Dict[str, Any] = None) -> str:
    """
    Create a formatted text export of the Q&A session.

    Args:
        qa_history: List of Q&A items
        session_info: Optional session metadata

    Returns:
        str: Formatted text for export
    """
    export_lines: List[str] = []

    # Header
    export_lines.append("=" * 60)
    export_lines.append("StudyMate - Q&A Session Export")
    export_lines.append("=" * 60)
    export_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Session metadata
    total_q = len(qa_history)
    export_lines.append(f"Total Questions: {total_q}")
    if session_info and session_info.get("files_processed"):
        try:
            files = session_info.get("files_processed", [])
            export_lines.append(f"Documents Processed: {', '.join(files)}")
        except Exception:
            pass

    export_lines.append("")

    # Q&A items
    for i, qa_item in enumerate(qa_history, 1):
        timestamp = qa_item.get("timestamp", datetime.now())
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except Exception:
                try:
                    # Fallback parse common formats
                    from datetime import datetime as _dt
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
                        try:
                            timestamp = _dt.strptime(timestamp, fmt)
                            break
                        except Exception:
                            continue
                    if isinstance(timestamp, str):
                        timestamp = datetime.now()
                except Exception:
                    timestamp = datetime.now()

        export_lines.append(f"Question {i} [{timestamp.strftime('%H:%M:%S')}]")
        export_lines.append("-" * 40)
        export_lines.append(f"Q: {qa_item.get('question', 'No question')}")
        export_lines.append("")
        export_lines.append(f"A: {qa_item.get('answer', 'No answer')}")
        export_lines.append("")

        # Sources
        sources = qa_item.get("sources", []) or []
        if sources:
            export_lines.append("Sources:")
            for j, source in enumerate(sources, 1):
                filename = source.get("filename", "Unknown")
                section = source.get("section", "Unknown section")
                export_lines.append(f"  {j}. {filename} - {section}")
            export_lines.append("")

        export_lines.append("=" * 60)
        export_lines.append("")

    # Footer
    export_lines.append("End of Session Export")
    export_lines.append(f"Total Questions Answered: {total_q}")

    return "\n".join(export_lines)


def create_qa_session_pdf_export(qa_history: List[Dict[str, Any]],
                                session_info: Dict[str, Any] = None):
    """
    Create a PDF export of the Q&A session.

    Args:
        qa_history: List of Q&A items
        session_info: Optional session metadata

    Returns:
        BytesIO buffer containing the PDF document or None if failed
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor
        import io

        # Create buffer
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#1e293b'),
            alignment=1  # Center alignment
        )

        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#3b82f6'),
            spaceBefore=20
        )

        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            textColor=HexColor('#1e293b'),
            fontName='Helvetica-Bold'
        )

        answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=16,
            textColor=HexColor('#374151'),
            leftIndent=20
        )

        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            textColor=HexColor('#6b7280'),
            alignment=1  # Center alignment
        )

        # Build content
        content = []

        # Title
        content.append(Paragraph("📚 StudyMate - Q&A Session", title_style))
        content.append(Spacer(1, 12))

        # Session info
        info_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        info_text += f"Total Questions: {len(qa_history)}"

        if session_info and "files_processed" in session_info:
            files = session_info['files_processed']
            if files:
                info_text += f"<br/>Documents: {', '.join(files)}"

        content.append(Paragraph(info_text, info_style))
        content.append(Spacer(1, 20))

        # Q&A items
        for i, qa_item in enumerate(qa_history, 1):
            # Question header
            content.append(Paragraph(f"Question {i}", header_style))

            # Question text
            question_text = qa_item.get('question', 'No question text')
            content.append(Paragraph(f"Q: {question_text}", question_style))

            # Answer text
            answer_text = qa_item.get('answer', 'No answer available')
            content.append(Paragraph(f"A: {answer_text}", answer_style))

            # Sources if available
            sources = qa_item.get('sources', [])
            if sources:
                sources_text = f"<i>Sources: {len(sources)} reference(s) from document</i>"
                content.append(Paragraph(sources_text, info_style))

            # Add spacing between Q&A pairs
            if i < len(qa_history):
                content.append(Spacer(1, 20))

        # Build PDF
        doc.build(content)
        buffer.seek(0)

        return buffer

    except ImportError:
        # ReportLab not available
        return None
    except Exception as e:
        print(f"Error creating Q&A PDF: {e}")
        return None
    
    

def get_session_stats(qa_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for the current session.
    
    Args:
        qa_history: List of Q&A items
        
    Returns:
        Dict: Session statistics
    """
    if not qa_history:
        return {
            "total_questions": 0,
            "avg_answer_length": 0,
            "session_duration": "0 minutes",
            "most_recent": None
        }
    
    total_questions = len(qa_history)
    
    # Calculate average answer length
    answer_lengths = [len(qa.get("answer", "")) for qa in qa_history]
    avg_answer_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
    
    # Calculate session duration
    timestamps = []
    for qa in qa_history:
        timestamp = qa.get("timestamp")
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    timestamps.append(datetime.fromisoformat(timestamp))
                except:
                    continue
            else:
                timestamps.append(timestamp)
    
    session_duration = "Unknown"
    if len(timestamps) >= 2:
        duration_minutes = (max(timestamps) - min(timestamps)).total_seconds() / 60
        session_duration = f"{duration_minutes:.1f} minutes"
    
    # Most recent question time
    most_recent = None
    if timestamps:
        most_recent = max(timestamps).strftime("%H:%M:%S")
    
    return {
        "total_questions": total_questions,
        "avg_answer_length": round(avg_answer_length, 1),
        "session_duration": session_duration,
        "most_recent": most_recent
    }


def clean_filename(filename: str) -> str:
    """
    Clean filename for safe display and processing.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Cleaned filename
    """
    if not filename:
        return "unknown_file"
    
    # Remove path components
    clean_name = os.path.basename(filename)
    
    # Remove or replace problematic characters
    clean_name = re.sub(r'[<>:"/\\|?*]', '_', clean_name)
    
    # Limit length
    if len(clean_name) > 50:
        name, ext = os.path.splitext(clean_name)
        clean_name = name[:45] + ext
    
    return clean_name


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def create_download_filename(base_name: str = "studymate_session", extension: str = "txt") -> str:
    """
    Create a timestamped filename for downloads.

    Args:
        base_name: Base name for the file
        extension: File extension (without dot)

    Returns:
        str: Timestamped filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


def log_user_action(action: str, details: Dict[str, Any] = None):
    """
    Log user actions for debugging and analytics.
    
    Args:
        action: Action name
        details: Optional action details
    """
    log_entry = f"User Action: {action}"
    if details:
        log_entry += f" | Details: {details}"
    
    logger.info(log_entry)
