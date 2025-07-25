import streamlit as st
import json
import pandas as pd
import requests
import io
import tempfile
import os
from datetime import datetime
import time

# Mock functions for demo
def mock_file_reader(rfp_url):
    return {
        "rfp_text": "Enterprise Network RFP - Requirements for secure, scalable network infrastructure...",
        "processed_files": ["Enterprise Network RFP document.pdf"],
        "status": "Processed 1 RFP files successfully"
    }

def mock_scorecard_builder(rfp_content):
    return {
        "technical_capability": {"points": 35},
        "cost_effectiveness": {"points": 25},
        "vendor_experience": {"points": 20},
        "implementation_approach": {"points": 20}
    }

def mock_multi_vendor_reader(vendor1_path, vendor2_path):
    return {
        "status": "success",
        "vendors": [
            {
                "vendor_name": "Cyberguard",
                "technical_data": {"security_compliance": True},
                "financial_data": {"tco_3year": "500000"},
                "vendor_data": {"years_in_business": "15"},
                "implementation_data": {"methodology": "agile"}
            },
            {
                "vendor_name": "SecureNet", 
                "technical_data": {"network_architecture": True},
                "financial_data": {"tco_3year": "450000"},
                "vendor_data": {"years_in_business": "12"},
                "implementation_data": {"methodology": "devops"}
            }
        ]
    }

def mock_scoring_engine(scorecard, vendor_data):
    return {
        "status": "success",
        "vendor_scores": [
            {
                "vendor_name": "Cyberguard",
                "total_score": 85.5,
                "total_possible": 100,
                "overall_percentage": 85.5,
                "grade": "A",
                "category_breakdown": {
                    "technical_capability": {"total_earned": 30, "total_possible": 35},
                    "cost_effectiveness": {"total_earned": 18, "total_possible": 25},
                    "vendor_experience": {"total_earned": 18, "total_possible": 20},
                    "implementation_approach": {"total_earned": 19.5, "total_possible": 20}
                }
            },
            {
                "vendor_name": "SecureNet",
                "total_score": 78.2,
                "total_possible": 100,
                "overall_percentage": 78.2,
                "grade": "B",
                "category_breakdown": {
                    "technical_capability": {"total_earned": 27, "total_possible": 35},
                    "cost_effectiveness": {"total_earned": 20, "total_possible": 25},
                    "vendor_experience": {"total_earned": 15, "total_possible": 20},
                    "implementation_approach": {"total_earned": 16.2, "total_possible": 20}
                }
            }
        ]
    }

def mock_executive_summary(scoring_results, industry_context):
    return {
        "executive_summary": "Cyberguard emerges as the recommended vendor with superior security capabilities and proven track record.",
        "strategic_analysis": "Strong technical architecture and security compliance framework align with enterprise requirements.",
        "decision_rationale": "85.5% overall score driven by exceptional security features and implementation methodology.",
        "risk_assessment": "Low risk profile with established vendor reputation and comprehensive security measures.",
        "implementation_roadmap": "12-month phased implementation with pilot deployment in Q1.",
        "financial_implications": "Higher initial investment offset by long-term security benefits and lower operational costs."
    }

# Streamlit App Configuration
st.set_page_config(
    page_title="Agentic RFX Orchestrator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        padding: 2rem 0;
        text-align: center;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 10px 10px;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .status-success {
        color: #10b981;
        font-weight: bold;
    }
    .status-warning {
        color: #f59e0b;
        font-weight: bold;
    }
    .status-error {
        color: #ef4444;
        font-weight: bold;
    }
    .vendor-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏢 Agentic RFX Orchestrator </h1>
    <p>Powered by Azure AI Foundry & PromptFlow</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'assessment_data' not in st.session_state:
    st.session_state.assessment_data = {}
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Sidebar Navigation
st.sidebar.title("🔧 Assessment Workflow")
steps = [
    "1️⃣ RFP Document Upload",
    "2️⃣ Vendor Proposals Upload", 
    "3️⃣ Industry Context",
    "4️⃣ Assessment & Scoring",
    "5️⃣ Executive Summary"
]

selected_step = st.sidebar.radio("Navigate to:", steps, index=st.session_state.current_step-1)
st.session_state.current_step = steps.index(selected_step) + 1

# Progress Bar
progress = st.session_state.current_step / len(steps)
st.sidebar.progress(progress)
st.sidebar.write(f"Progress: {int(progress * 100)}%")

# Main Content Area
if st.session_state.current_step == 1:
    st.header("📄 Step 1: RFP Document Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload RFP Documents")
        
        # File upload options
        upload_method = st.radio("Choose upload method:", 
                                ["File Upload", "Azure Blob URL"])
        
        if upload_method == "File Upload":
            uploaded_files = st.file_uploader(
                "Choose RFP documents",
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True,
                help="Upload your RFP documents in PDF, DOCX, or TXT format"
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
                for file in uploaded_files:
                    st.write(f"📁 {file.name} ({file.size} bytes)")
        
        else:
            rfp_url = st.text_input(
                "Enter Azure Blob Storage URL:",
                placeholder="https://your-storage.blob.core.windows.net/...",
                help="Provide the direct URL to your RFP document in Azure Blob Storage"
            )
            
            if rfp_url:
                if st.button("🔍 Validate URL"):
                    try:
                        # Mock validation
                        st.success("✅ URL is accessible")
                        st.session_state.assessment_data['rfp_url'] = rfp_url
                    except:
                        st.error("❌ URL is not accessible")
        
        # Process RFP
        if st.button("🚀 Process RFP Documents", type="primary"):
            with st.spinner("Processing RFP documents..."):
                time.sleep(2)  # Simulate processing
                
                # Mock processing
                rfp_result = mock_file_reader(rfp_url if upload_method == "Azure Blob URL" else "uploaded_files")
                
                st.session_state.assessment_data['rfp_processed'] = rfp_result
                st.success("✅ RFP documents processed successfully!")
                
                # Show results
                st.json(rfp_result)
    
    with col2:
        st.subheader("📋 Requirements Checklist")
        
        checklist_items = [
            "Technical specifications",
            "Security requirements", 
            "Performance criteria",
            "Compliance standards",
            "Budget constraints",
            "Timeline expectations"
        ]
        
        for item in checklist_items:
            st.checkbox(item, key=f"req_{item}")
        
        st.info("💡 **Tip:** Ensure your RFP contains clear evaluation criteria for better assessment results.")

elif st.session_state.current_step == 2:
    st.header("🏢 Step 2: Vendor Proposals Upload")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vendor 1: Cyberguard")
        
        vendor1_method = st.radio("Upload method for Cyberguard:", 
                                 ["File Upload", "Azure Blob URL"], key="v1_method")
        
        if vendor1_method == "File Upload":
            vendor1_files = st.file_uploader(
                "Cyberguard proposal documents",
                type=['pdf', 'docx'],
                accept_multiple_files=True,
                key="vendor1_upload"
            )
        else:
            vendor1_url = st.text_input(
                "Cyberguard Azure Blob URL:",
                placeholder="https://storage.blob.../Cyberguard/",
                key="vendor1_url"
            )
    
    with col2:
        st.subheader("Vendor 2: SecureNet")
        
        vendor2_method = st.radio("Upload method for SecureNet:", 
                                 ["File Upload", "Azure Blob URL"], key="v2_method")
        
        if vendor2_method == "File Upload":
            vendor2_files = st.file_uploader(
                "SecureNet proposal documents",
                type=['pdf', 'docx'],
                accept_multiple_files=True,
                key="vendor2_upload"
            )
        else:
            vendor2_url = st.text_input(
                "SecureNet Azure Blob URL:",
                placeholder="https://storage.blob.../SecureNet/",
                key="vendor2_url"
            )
    
    # Process vendor proposals
    if st.button("🔄 Process Vendor Proposals", type="primary"):
        with st.spinner("Processing vendor proposals..."):
            time.sleep(3)  # Simulate processing
            
            # Mock processing
            vendor_result = mock_multi_vendor_reader("vendor1_path", "vendor2_path")
            
            st.session_state.assessment_data['vendors_processed'] = vendor_result
            st.success("✅ Vendor proposals processed successfully!")
            
            # Display vendor summary
            for vendor in vendor_result['vendors']:
                with st.expander(f"📊 {vendor['vendor_name']} Summary"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Experience", vendor['vendor_data']['years_in_business'] + " years")
                    with col2:
                        st.metric("Cost", "$" + vendor['financial_data']['tco_3year'])
                    with col3:
                        st.metric("Methodology", vendor['implementation_data']['methodology'].title())

elif st.session_state.current_step == 3:
    st.header("🏭 Step 3: Industry Context & Knowledge Base")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Industry Configuration")
        
        industry = st.selectbox(
            "Select Industry:",
            ["Technology", "Financial Services", "Healthcare", "Manufacturing", "Government"],
            help="Choose the industry sector for specialized compliance and standards"
        )
        
        rfp_type = st.selectbox(
            "RFP Type:",
            ["Enterprise Network", "Software Solution", "Infrastructure", "Security Services", "Cloud Migration"],
            help="Specify the type of RFP for targeted evaluation criteria"
        )
        
        # Advanced options
        with st.expander("🔧 Advanced Configuration"):
            mcp_server = st.text_input(
                "MCP Server URL (Optional):",
                placeholder="https://mcp-foundry.azurewebsites.net",
                help="Custom MCP server for specialized industry knowledge"
            )
            
            use_local_kb = st.checkbox(
                "Use Local Knowledge Base",
                value=True,
                help="Fallback to local knowledge if MCP server is unavailable"
            )
        
        if st.button("🧠 Load Industry Context", type="primary"):
            with st.spinner("Loading industry knowledge and standards..."):
                time.sleep(2)
                
                # Mock industry context
                industry_context = {
                    "industry": industry,
                    "rfp_type": rfp_type,
                    "scorecard_parameters": [
                        {"criteria": "Technical Architecture", "weight": 25},
                        {"criteria": "Security & Compliance", "weight": 20},
                        {"criteria": "Performance & Scalability", "weight": 15},
                        {"criteria": "Integration Capabilities", "weight": 15},
                        {"criteria": "Support & Maintenance", "weight": 15},
                        {"criteria": "Cost Effectiveness", "weight": 10}
                    ],
                    "compliance_requirements": [
                        "ISO 27001 certification",
                        "SOC 2 Type II compliance",
                        "Data encryption standards",
                        "Regular security assessments"
                    ]
                }
                
                st.session_state.assessment_data['industry_context'] = industry_context
                st.success("✅ Industry context loaded successfully!")
                
                # Build scorecard
                scorecard = mock_scorecard_builder(st.session_state.assessment_data.get('rfp_processed', {}))
                st.session_state.assessment_data['scorecard'] = scorecard
    
    with col2:
        st.subheader("📊 Industry Standards")
        
        if 'industry_context' in st.session_state.assessment_data:
            context = st.session_state.assessment_data['industry_context']
            
            st.write("**Evaluation Criteria:**")
            for param in context['scorecard_parameters']:
                st.write(f"• {param['criteria']} ({param['weight']}%)")
            
            st.write("**Compliance Requirements:**")
            for req in context['compliance_requirements']:
                st.write(f"• {req}")
        else:
            st.info("Load industry context to see standards and requirements.")

elif st.session_state.current_step == 4:
    st.header("🎯 Step 4: Assessment & Scoring")
    
    # Check prerequisites
    if 'scorecard' not in st.session_state.assessment_data:
        st.warning("⚠️ Please complete previous steps first.")
        st.stop()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔍 Run Assessment")
        
        assessment_options = st.multiselect(
            "Assessment Categories:",
            ["Technical Capability", "Cost Effectiveness", "Vendor Experience", "Implementation Approach"],
            default=["Technical Capability", "Cost Effectiveness", "Vendor Experience", "Implementation Approach"]
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold:",
            min_value=50,
            max_value=95,
            value=75,
            help="Minimum confidence level for recommendations"
        )
        
        if st.button("🚀 Run Complete Assessment", type="primary"):
            with st.spinner("Running comprehensive assessment..."):
                progress_bar = st.progress(0)
                
                # Simulate assessment steps
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                # Mock scoring
                scoring_results = mock_scoring_engine(
                    st.session_state.assessment_data['scorecard'],
                    st.session_state.assessment_data.get('vendors_processed', {})
                )
                
                st.session_state.assessment_data['scoring_results'] = scoring_results
                st.success("✅ Assessment completed successfully!")
    
    with col2:
        st.subheader("📈 Live Results")
        
        if 'scoring_results' in st.session_state.assessment_data:
            results = st.session_state.assessment_data['scoring_results']
            
            # Create simple bar chart using Streamlit's built-in chart
            vendor_names = [v['vendor_name'] for v in results['vendor_scores']]
            scores = [v['total_score'] for v in results['vendor_scores']]
            
            # Create DataFrame for chart
            chart_data = pd.DataFrame({
                'Vendor': vendor_names,
                'Score': scores
            })
            
            st.subheader("Vendor Comparison")
            st.bar_chart(chart_data.set_index('Vendor'))
            
            # Score breakdown
            for vendor in results['vendor_scores']:
                with st.expander(f"📊 {vendor['vendor_name']} - {vendor['total_score']}/100"):
                    categories = vendor['category_breakdown']
                    for cat_name, cat_data in categories.items():
                        earned = cat_data['total_earned']
                        possible = cat_data['total_possible']
                        percentage = (earned/possible) * 100 if possible > 0 else 0
                        st.metric(
                            cat_name.replace('_', ' ').title(),
                            f"{earned:.1f}/{possible}",
                            f"{percentage:.1f}%"
                        )

elif st.session_state.current_step == 5:
    st.header("📋 Step 5: Executive Summary & Recommendations")
    
    if 'scoring_results' not in st.session_state.assessment_data:
        st.warning("⚠️ Please complete the assessment first.")
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("📄 Generate Executive Summary", type="primary"):
            with st.spinner("Generating executive summary..."):
                time.sleep(2)
                
                # Mock executive summary
                exec_summary = mock_executive_summary(
                    st.session_state.assessment_data['scoring_results'],
                    st.session_state.assessment_data.get('industry_context', {})
                )
                
                st.session_state.assessment_data['executive_summary'] = exec_summary
        
        if 'executive_summary' in st.session_state.assessment_data:
            summary = st.session_state.assessment_data['executive_summary']
            
            st.subheader("📄 Executive Summary")
            st.write(summary['executive_summary'])
            
            st.subheader("🎯 Strategic Analysis")
            st.write(summary['strategic_analysis'])
            
            st.subheader("⚖️ Decision Rationale")
            st.write(summary['decision_rationale'])
            
            st.subheader("⚠️ Risk Assessment")
            st.write(summary['risk_assessment'])
            
            st.subheader("🗺️ Implementation Roadmap")
            st.write(summary['implementation_roadmap'])
            
            st.subheader("💰 Financial Implications")
            st.write(summary['financial_implications'])
    
    with col2:
        st.subheader("📊 Final Metrics")
        
        if 'scoring_results' in st.session_state.assessment_data:
            results = st.session_state.assessment_data['scoring_results']
            winner = max(results['vendor_scores'], key=lambda x: x['total_score'])
            
            st.metric("🏆 Recommended Vendor", winner['vendor_name'])
            st.metric("📈 Winning Score", f"{winner['total_score']}/100")
            st.metric("📊 Grade", winner['grade'])
            
            # Download options
            st.subheader("📥 Export Results")
            
            if st.button("📄 Download PDF Report"):
                st.success("PDF report generated! (Mock)")
            
            if st.button("📊 Download Excel Analysis"):
                st.success("Excel file generated! (Mock)")
            
            if st.button("📋 Download JSON Data"):
                st.download_button(
                    label="Download Assessment Data",
                    data=json.dumps(st.session_state.assessment_data, indent=2),
                    file_name=f"rfx_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.9em;">
    🚀 Powered by Azure AI Foundry | Built with Streamlit | 
    <a href="#" style="color: #3b82f6;">Documentation</a> | 
    <a href="#" style="color: #3b82f6;">Support</a>
</div>
""", unsafe_allow_html=True)
