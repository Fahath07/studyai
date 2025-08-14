# IBM Watsonx Setup Guide

## 🚀 Get Real AI-Powered Responses with IBM Watsonx

Follow these steps to enable full AI functionality in StudyMate:

### Step 1: Create IBM Cloud Account

1. **Sign up**: Go to https://cloud.ibm.com/registration
2. **Verify email**: Check your email and verify your account
3. **Login**: Access the IBM Cloud dashboard

### Step 2: Create Watsonx.ai Instance

1. **Navigate to Catalog**: Click "Catalog" in the top menu
2. **Search for Watsonx**: Type "watsonx.ai" in the search box
3. **Select Service**: Click on "watsonx.ai" service
4. **Choose Plan**: 
   - **Lite Plan**: Free tier with limited usage (good for testing)
   - **Standard Plan**: Pay-as-you-go (recommended for regular use)
5. **Create Instance**: Click "Create"

### Step 3: Get Your Credentials

#### Get API Key:
1. **Go to Manage**: Click "Manage" in the top menu
2. **Access (IAM)**: Select "Access (IAM)"
3. **API Keys**: Click "API keys" in the left sidebar
4. **Create**: Click "Create an IBM Cloud API key"
5. **Name**: Give it a name like "StudyMate-API-Key"
6. **Copy**: Copy the API key (save it securely!)

#### Get Project ID:
1. **Open Watsonx**: Go to your watsonx.ai instance
2. **Create Project**: Click "Create a project" or use existing
3. **Project Settings**: Click on project settings/manage
4. **Copy Project ID**: Find and copy the Project ID

#### Get URL:
Your URL will be based on your region:
- **US South**: `https://us-south.ml.cloud.ibm.com`
- **EU Germany**: `https://eu-de.ml.cloud.ibm.com`
- **Japan**: `https://jp-tok.ml.cloud.ibm.com`

### Step 4: Configure StudyMate

Edit your `.env` file with the real credentials:

```env
# IBM Watsonx.ai Configuration
IBM_API_KEY=your_actual_api_key_here
IBM_PROJECT_ID=your_actual_project_id_here
IBM_URL=https://us-south.ml.cloud.ibm.com

# Model Configuration
MODEL_ID=mistralai/mixtral-8x7b-instruct-v01
MAX_NEW_TOKENS=500
TEMPERATURE=0.3
```

### Step 5: Test Connection

Run this test to verify your setup:

```bash
python -c "
from watsonx_integration import initialize_watsonx_client
client = initialize_watsonx_client()
if client and hasattr(client, 'test_connection'):
    if client.test_connection():
        print('✅ IBM Watsonx connected successfully!')
    else:
        print('❌ Connection failed - check credentials')
else:
    print('⚠️ Running in demo mode - check .env file')
"
```

### Step 6: Restart Application

```bash
# Stop current application (Ctrl+C)
streamlit run streamlit_app.py
```

## 🔧 Troubleshooting

### "Error getting IAM Token"
- **Check API Key**: Ensure it's copied correctly without extra spaces
- **Check Permissions**: API key must have access to watsonx.ai
- **Check Region**: URL must match your instance region

### "Project not found"
- **Verify Project ID**: Copy from watsonx.ai project settings
- **Check Access**: Ensure API key has access to the project

### "Model not available"
- **Check Model ID**: Verify the model name is correct
- **Check Region**: Some models may not be available in all regions

## 💰 Cost Considerations

### Lite Plan (Free):
- **Capacity Units**: 25 per month
- **Good for**: Testing and light usage
- **Limitations**: Limited requests per month

### Standard Plan:
- **Pay-per-use**: ~$0.002 per 1K tokens
- **Good for**: Regular usage
- **Estimate**: 1000 questions ≈ $2-5 depending on length

## 🎯 Expected Results

With IBM Watsonx configured, you'll get:
- **Advanced AI responses**: Natural, contextual answers
- **Better reasoning**: Complex question handling
- **Improved accuracy**: More precise information extraction
- **Professional quality**: Enterprise-grade AI capabilities

---

**Once configured, StudyMate will provide professional-grade AI responses! 🚀**
