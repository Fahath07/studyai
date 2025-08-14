# StudyMate Usage Instructions

## 🚀 Quick Start Guide

### 1. **Upload Your PDFs**
- Click on the "📄 Upload Academic PDFs" section
- Drag and drop your PDF files or click "Browse files"
- Supported files: PDF documents (lecture notes, textbooks, research papers)
- Click "Process PDFs" to extract text and build the search index

### 2. **Ask Questions**
- Once PDFs are processed, go to the "❓ Ask Questions" section
- Type your question in natural language
- Examples:
  - "What is machine learning?"
  - "Explain the main concepts in chapter 3"
  - "What are the key differences between supervised and unsupervised learning?"
- Click "Get Answer" to receive a response

### 3. **View Results**
- Get AI-generated answers based on your documents
- See source references showing which parts of your PDFs were used
- Review the "Referenced Paragraphs" section to see exact text excerpts

### 4. **Session Management**
- View your Q&A history in the right panel
- Download your session as a text file for offline study
- Clear loaded files to start fresh with new documents

## 🔧 Configuration Modes

### Demo Mode (Default)
- **What it is**: StudyMate runs without IBM Watsonx credentials
- **Features available**:
  - ✅ PDF upload and text extraction
  - ✅ Document search and retrieval
  - ✅ Basic demo responses
- **Limitations**: Responses are pre-written examples, not AI-generated

### Full AI Mode (Requires IBM Watsonx)
- **What it is**: Full AI-powered responses using IBM Watsonx
- **Setup required**:
  1. Get IBM Watsonx credentials (API key, Project ID, URL)
  2. Edit the `.env` file with your credentials
  3. Restart the application
- **Features**:
  - ✅ All demo mode features
  - ✅ AI-generated answers using IBM's Mixtral model
  - ✅ Context-aware responses based on your documents

## 📋 Troubleshooting

### "No text could be extracted from PDF"
**Possible causes:**
- Scanned PDFs (images of text, not actual text)
- Password-protected PDFs
- Corrupted PDF files
- PDFs with only images/graphics

**Solutions:**
- Try a different PDF with actual text content
- Use OCR software to convert scanned PDFs to text-based PDFs
- Remove password protection from PDFs

### "Watsonx client not initialized"
**Cause:** IBM Watsonx credentials not configured

**Solution:**
1. Edit the `.env` file in the project directory
2. Replace placeholder values with your actual credentials:
   ```
   IBM_API_KEY=your_actual_api_key
   IBM_PROJECT_ID=your_actual_project_id
   IBM_URL=your_actual_instance_url
   ```
3. Restart the application

### "No relevant content found"
**Cause:** Your question doesn't match content in uploaded PDFs

**Solutions:**
- Try rephrasing your question
- Use keywords that appear in your documents
- Check if the PDF text was extracted correctly
- Upload more relevant documents

## 💡 Tips for Best Results

### PDF Upload Tips
- Use text-based PDFs (not scanned images)
- Ensure PDFs are not password-protected
- Academic papers and textbooks work best
- Multiple related documents improve answer quality

### Question Tips
- Be specific about what you want to know
- Use keywords from your documents
- Ask one question at a time
- Try different phrasings if you don't get good results

### Document Organization
- Upload related documents together
- Use descriptive filenames
- Keep documents focused on similar topics
- Remove unnecessary pages if possible

## 🔒 Privacy & Security

- **Local Processing**: All PDF processing happens on your computer
- **No Data Storage**: Your documents are not permanently stored
- **Session-based**: Data is cleared when you close the application
- **IBM Watsonx**: If configured, questions and context are sent to IBM's servers for AI processing

## 📞 Support

If you encounter issues:
1. Check the error messages in the application
2. Review the troubleshooting section above
3. Check the terminal/console for detailed error logs
4. Ensure all dependencies are installed correctly

## 🎯 Example Workflow

1. **Start the application**: `streamlit run streamlit_app.py`
2. **Upload PDFs**: Add your course materials or research papers
3. **Wait for processing**: Let the system extract text and build the search index
4. **Ask questions**: Start with broad questions, then get more specific
5. **Review answers**: Check the source references to verify information
6. **Export session**: Download your Q&A history for later review

---

**Happy studying with StudyMate! 📚🤖**
