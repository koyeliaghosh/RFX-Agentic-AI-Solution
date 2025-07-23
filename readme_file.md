# 🏢 RFX Proposal Assessment Automation

An intelligent RFP/RFX evaluation system powered by Azure AI Foundry, PromptFlow, and Streamlit. This tool automates vendor proposal assessment, scoring, and executive summary generation for enterprise procurement decisions.

## 🚀 Features

- **📄 Multi-format Document Processing**: Supports PDF, DOCX, and TXT files
- **🤖 AI-Powered Scorecard Generation**: Automatically creates evaluation criteria based on RFP requirements
- **🏢 Multi-Vendor Analysis**: Compare proposals from multiple vendors simultaneously
- **🏭 Industry-Specific Knowledge**: Contextual evaluation based on industry standards and compliance requirements
- **📊 Interactive Scoring Engine**: Real-time assessment with visual comparisons
- **📋 Executive Summary Generation**: AI-generated recommendations and strategic analysis
- **☁️ Azure Integration**: Seamless integration with Azure AI Foundry and Blob Storage

## 🏗️ Architecture

The solution consists of 6 core components:

1. **File Reader** (`File_Reader_Function.py`) - Document parsing and content extraction
2. **Scorecard Builder** (LLM) - Dynamic evaluation criteria generation
3. **Multi-Vendor Reader** (`Multi_Vendor_Reader.py`) - Vendor proposal processing
4. **Scoring Engine** (`Sxoring_Engine.py`) - Automated scoring and comparison
5. **Industry Knowledge Base** (`MCP_LocalIndustryKB.py`) - MCP-powered industry context
6. **Executive Summary** (LLM) - Strategic recommendations generation

## 🎯 Demo

### Live Demo
🌐 **[Try the live demo on Streamlit Cloud](https://your-app-url.streamlit.app)**

### Screenshots
The application provides a 5-step workflow:

1. **RFP Upload** - Document upload and processing
2. **Vendor Proposals** - Multi-vendor document ingestion
3. **Industry Context** - Standards and compliance configuration
4. **Assessment & Scoring** - Real-time evaluation with charts
5. **Executive Summary** - Strategic recommendations and reporting

## 🚀 Quick Start

### Option 1: Streamlit Cloud (Recommended for Demo)

1. **Fork this repository**
2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository
   - Deploy!

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/rfx-agentic-ai-solution.git
cd rfx-agentic-ai-solution

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_rfx_ui.py
```

The app will open in your browser at `http://localhost:8501`

### Option 3: Azure Container Deployment

For production deployment on Azure Container Apps:

```bash
# Make the deployment script executable
chmod +x deploy_azure.sh

# Configure your Azure credentials
az login

# Run deployment script
./deploy_azure.sh
```

## 📋 Requirements

### Basic Requirements (Demo Mode)
```
streamlit
pandas
requests
```

### Full Requirements (Production)
```
streamlit>=1.28.0
pandas>=1.5.0
requests>=2.28.0
PyPDF2>=3.0.0
python-docx>=0.8.11
azure-ai-projects>=1.0.0b3
azure-identity>=1.15.0
azure-storage-blob>=12.19.0
promptflow>=1.8.0
```

## ⚙️ Configuration

### Environment Variables

For production deployment with Azure AI Foundry:

```bash
# Azure AI Foundry Configuration
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-foundry-endpoint
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group

# Azure Storage (Optional)
AZURE_STORAGE_CONNECTION_STRING=your-storage-connection-string

# MCP Server (Optional)
INDUSTRY_MCP_SERVER_URL=https://mcp-foundry.azurewebsites.net
```

### Azure AI Foundry Setup

1. **Create AI Foundry Project**:
   - Go to [Azure AI Foundry](https://ai.azure.com)
   - Create new project
   - Deploy GPT-4 model

2. **Configure PromptFlow**:
   - Import the provided flow definitions
   - Connect to your deployed models
   - Test individual components

3. **Set up Blob Storage** (Optional):
   - Create storage account
   - Configure containers for RFP documents
   - Update connection strings

## 📁 File Structure

```
rfx-agentic-ai-solution/
├── streamlit_rfx_ui.py          # Main Streamlit application
├── requirements.txt             # Python dependencies
├── functions/                   # PromptFlow functions
│   ├── File_Reader_Function.py
│   ├── Multi_Vendor_Reader.py
│   ├── Sxoring_Engine.py
│   ├── MCP_LocalIndustryKB.py
│   └── Executive_Summary_updated.py
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   └── deploy_azure.sh
├── docs/                        # Documentation
│   ├── USER_GUIDE.md
│   └── API_REFERENCE.md
└── README.md
```

## 🔧 Usage Guide

### Step 1: RFP Document Upload
- Upload RFP documents via file upload or Azure Blob URL
- Supports multiple document formats
- Automatic content extraction and processing

### Step 2: Vendor Proposals Upload
- Upload proposals from multiple vendors
- Side-by-side document processing
- Automatic feature extraction

### Step 3: Industry Context Configuration
- Select industry (Technology, Finance, Healthcare, etc.)
- Choose RFP type (Network, Software, Infrastructure, etc.)
- Load industry-specific standards and compliance requirements

### Step 4: Assessment & Scoring
- Automated scoring based on extracted criteria
- Real-time comparison charts
- Detailed category breakdowns
- Confidence scoring

### Step 5: Executive Summary
- AI-generated strategic recommendations
- Risk assessment and mitigation strategies
- Implementation roadmap
- Financial impact analysis
- Export options (PDF, Excel, JSON)

## 🎨 Customization

### Adding New Industries
Edit `MCP_LocalIndustryKB.py` to add industry-specific knowledge:

```python
industry_knowledge = {
    "your_industry": {
        "scorecard_parameters": [...],
        "compliance_requirements": [...],
        "industry_benchmarks": {...}
    }
}
```

### Custom Scoring Criteria
Modify `Sxoring_Engine.py` to adjust scoring algorithms:

```python
def calculate_custom_score(criteria, data, vendor_name):
    # Your custom scoring logic
    return score_result
```

### UI Customization
Update `streamlit_rfx_ui.py` to modify the interface:

```python
# Custom CSS
st.markdown("""
<style>
    .your-custom-class {
        /* Your styles */
    }
</style>
""", unsafe_allow_html=True)
```

## 🧪 Testing

### Running Tests
```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# UI tests
streamlit run streamlit_rfx_ui.py --server.headless=true
```

### Sample Data
Test with provided sample documents in `tests/sample_data/`:
- `sample_rfp.pdf`
- `vendor_proposals/cyberguard_proposal.pdf`
- `vendor_proposals/securenet_proposal.pdf`

## 🚀 Deployment Options

### 1. Streamlit Cloud (Free)
- Perfect for demos and prototyping
- Automatic deployment from GitHub
- No infrastructure management

### 2. Azure Container Apps (Production)
- Scalable container deployment
- Integrated with Azure AI services
- Custom domain and SSL support

### 3. Docker (Self-hosted)
```bash
# Build container
docker build -t rfx-assessment .

# Run container
docker run -p 8080:8080 rfx-assessment
```

## 📊 Performance & Scalability

- **Document Processing**: ~2-5 seconds per document
- **Scoring Engine**: ~10-30 seconds for complete assessment
- **Concurrent Users**: Up to 50 users (Azure Container Apps)
- **Document Size Limit**: 50MB per file
- **Supported Formats**: PDF, DOCX, TXT

## 🔒 Security & Compliance

- **Data Encryption**: All data encrypted in transit and at rest
- **Azure Identity**: Integrated Azure AD authentication
- **Privacy**: No document content stored permanently
- **Compliance**: SOC 2, ISO 27001 compatible with Azure services

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Solution: Install requirements
   pip install -r requirements.txt
   ```

2. **Azure Authentication**
   ```bash
   # Solution: Login to Azure CLI
   az login
   ```

3. **Document Processing Fails**
   - Check file format compatibility
   - Verify document is not password-protected
   - Ensure file size is under 50MB

4. **Streamlit Cloud Deployment**
   - Verify requirements.txt is in root directory
   - Check for Python version compatibility
   - Review deployment logs in Streamlit Cloud dashboard

### Performance Optimization

- Use Azure Blob Storage for large documents
- Enable caching for repeated assessments
- Consider Premium Azure AI Foundry tier for higher throughput

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatting
black .
flake8 .

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/rfx-agentic-ai-solution/issues)
- **Email**: support@your-domain.com
- **Community**: [Discord](https://discord.gg/your-server)

## 🏆 Acknowledgments

- **Azure AI Foundry** - For the AI/ML platform
- **Streamlit** - For the web application framework
- **PromptFlow** - For the orchestration engine
- **Community Contributors** - For feedback and improvements

## 🗺️ Roadmap

### Version 2.0 (Q2 2025)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Automated reporting
- [ ] Integration with procurement systems

### Version 2.1 (Q3 2025)
- [ ] Mobile application
- [ ] API endpoints
- [ ] Bulk processing capabilities
- [ ] Advanced ML models

---

**Made with ❤️ by [Your Name/Team]**

*Transforming procurement decisions through AI-powered assessment*