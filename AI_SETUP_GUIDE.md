# StudyMate AI Setup Guide

## 🚀 Get Real AI-Powered Responses

StudyMate now supports multiple AI providers for generating detailed, intelligent answers from your PDF documents. Choose the option that works best for you:

## 🎯 Quick Setup Options

### Option 1: IBM Watsonx (Recommended for Production)
- **Best for**: Professional use, enterprise features
- **Cost**: Free tier available, then pay-per-use
- **Quality**: Highest quality responses
- **Setup time**: 10-15 minutes

### Option 2: Hugging Face (Free Alternative)
- **Best for**: Personal use, experimentation
- **Cost**: Completely free (local models)
- **Quality**: Good quality responses
- **Setup time**: 5-10 minutes

### Option 3: Auto Mode (Recommended)
- **Best for**: Beginners, automatic selection
- **Tries**: IBM Watsonx → Hugging Face → Demo Mode
- **Setup**: Configure any of the above, app chooses best available

---

## 🔧 Option 1: IBM Watsonx Setup

### Step 1: Get IBM Cloud Account
1. **Sign up**: https://cloud.ibm.com/registration
2. **Verify email** and login to dashboard

### Step 2: Create Watsonx Instance
1. **Catalog** → Search "watsonx.ai"
2. **Select service** → Choose plan:
   - **Lite**: Free (25 capacity units/month)
   - **Standard**: Pay-per-use (~$0.002/1K tokens)
3. **Create instance**

### Step 3: Get Credentials
1. **API Key**: Manage → Access (IAM) → API keys → Create
2. **Project ID**: Open watsonx → Project settings → Copy ID
3. **URL**: Based on region:
   - US South: `https://us-south.ml.cloud.ibm.com`
   - EU Germany: `https://eu-de.ml.cloud.ibm.com`

### Step 4: Configure StudyMate
Edit `.env` file:
```env
IBM_API_KEY=your_actual_api_key
IBM_PROJECT_ID=your_actual_project_id  
IBM_URL=https://us-south.ml.cloud.ibm.com
```

---

## 🤗 Option 2: Hugging Face Setup

### Step 1: Install Dependencies
```bash
pip install transformers torch accelerate
```

### Step 2: Optional - Get API Token (for faster models)
1. **Sign up**: https://huggingface.co/join
2. **Get token**: Settings → Access Tokens → New token
3. **Add to .env**:
```env
HUGGINGFACE_API_TOKEN=your_token_here
```

### Step 3: Choose Model Type
- **Local Models**: Run on your computer (free, slower)
- **API Models**: Run on Hugging Face servers (free tier, faster)

---

## ⚡ Quick Start Instructions

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 2. Choose Your AI Provider
In the StudyMate sidebar:
1. **Select AI Provider**: Choose from dropdown
2. **Click "Initialize AI"**: Set up the selected provider
3. **Check status**: Green checkmark = ready to use

### 3. Test with Questions
1. **Upload PDFs**: Process your documents
2. **Ask questions**: Get AI-powered responses
3. **Compare providers**: Try different AI options

---

## 🎛️ AI Provider Comparison

| Feature | IBM Watsonx | Hugging Face | Demo Mode |
|---------|-------------|--------------|-----------|
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost** | 💰 Pay-per-use | 🆓 Free | 🆓 Free |
| **Setup** | 🔧 Medium | 🔧 Easy | ✅ None |
| **Reasoning** | 🧠 Advanced | 🧠 Good | 🧠 Basic |
| **Offline** | ❌ No | ✅ Yes | ✅ Yes |

---

## 🛠️ Troubleshooting

### IBM Watsonx Issues
- **"Error getting IAM Token"**: Check API key format
- **"Project not found"**: Verify Project ID
- **"Model not available"**: Check region/model compatibility

### Hugging Face Issues
- **"Model loading failed"**: Try smaller model (distilgpt2)
- **"CUDA out of memory"**: Use CPU mode or smaller model
- **"Slow responses"**: Consider using API token

### General Issues
- **"No AI provider active"**: Click "Initialize AI" in sidebar
- **"Blank responses"**: Check model initialization logs
- **"Connection timeout"**: Check internet connection

---

## 📊 Expected Performance

### Response Quality Examples

**Question**: "What is machine learning?"

**IBM Watsonx**: 
> "Machine learning is a sophisticated subset of artificial intelligence that enables computer systems to automatically learn and improve their performance on specific tasks through experience, without being explicitly programmed for each scenario..."

**Hugging Face**:
> "Machine learning is a method of data analysis that automates analytical model building. It uses algorithms that iteratively learn from data, allowing computers to find hidden insights..."

**Demo Mode**:
> "Based on the uploaded documents: Machine learning is a method of data analysis that automates analytical model building..."

---

## 🚀 Next Steps

1. **Choose your provider** based on needs and budget
2. **Follow setup instructions** for your chosen option
3. **Test with sample PDFs** to verify functionality
4. **Experiment with different question types**
5. **Compare response quality** across providers

---

**Ready to get intelligent answers from your PDFs! 🎯📚**

For detailed setup instructions, see:
- `IBM_WATSONX_SETUP.md` - Complete IBM Watsonx guide
- `HUGGINGFACE_SETUP.md` - Hugging Face configuration
- `USAGE_INSTRUCTIONS.md` - How to use the application
