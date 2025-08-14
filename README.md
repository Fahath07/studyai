# StudyMate - AI-Powered Academic PDF RAG System

StudyMate is a Retrieval-Augmented Generation (RAG) system that allows students to upload academic PDFs and ask questions in natural language, receiving grounded, source-referenced answers.

## Features

- **Multi-PDF Upload**: Upload multiple academic PDFs (lecture notes, textbooks, research papers)
- **Intelligent Chunking**: Text extraction with overlapping chunks for context retention
- **Semantic Search**: Uses SentenceTransformers + FAISS for relevant content retrieval
- **AI-Powered Answers**: IBM Watsonx LLM integration for accurate, grounded responses
- **Source References**: All answers include references to original document sections
- **Session History**: Maintains Q&A history with export functionality
- **Academic UI**: Clean, minimalist interface designed for students

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
1. Copy `.env.template` to `.env`
2. Fill in your IBM Watsonx credentials:
   - `IBM_API_KEY`: Your IBM Cloud API key
   - `IBM_PROJECT_ID`: Your Watsonx project ID
   - `IBM_URL`: Your Watsonx instance URL

### 3. Run the Application
```bash
streamlit run streamlit_app.py
```

## Usage

1. **Upload PDFs**: Drag and drop your academic PDFs into the upload area
2. **Ask Questions**: Type your question in natural language
3. **Get Answers**: Receive AI-generated answers with source references
4. **Review History**: View all previous Q&A pairs
5. **Export Session**: Download your Q&A history as a text file

## Technical Architecture

- **Frontend**: Streamlit web interface
- **PDF Processing**: PyMuPDF for text extraction
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Search**: FAISS IndexFlatL2
- **LLM**: IBM Watsonx (mistralai/mixtral-8x7b-instruct-v01)
- **Environment**: python-dotenv for configuration

## File Structure

```
StudyMate/
├── streamlit_app.py          # Main Streamlit application
├── pdf_processing.py         # PDF extraction and chunking
├── embedding_retrieval.py    # Embedding generation and FAISS retrieval
├── watsonx_integration.py    # IBM Watsonx API integration
├── utils.py                  # Utility functions
├── requirements.txt          # Python dependencies
├── .env.template            # Environment variables template
└── README.md               # This file
```

## Requirements

- Python 3.10+
- IBM Watsonx.ai account with API access
- Internet connection for LLM API calls
