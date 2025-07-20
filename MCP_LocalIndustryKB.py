# hybrid_mcp_integration.py - Updated for Enterprise Network RFP
from promptflow import tool
import json
import os
import requests
from typing import Dict, Any
import PyPDF2
import io

@tool
def get_industry_context_hybrid(
    rfp_document_url: str = "https://rfxagentichub9781132764.blob.core.windows.net/71693736-86ed-47c3-8342-4ce83deff0c6-azureml-blobstore/UI/2025-06-26_153459_UTC/RFP%20Documents/Enterprise%20Network%20/Enterprise%20Network%20RFP%20document.pdf",
    vendor_proposal_1_url: str = "https://rfxagentichub9781132764.blob.core.windows.net/71693736-86ed-47c3-8342-4ce83deff0c6-azureml-blobstore/UI/2025-06-26_153459_UTC/Vendor_Proposals/Cyberguard%20/Cyberguard%20solution_network%20response.pdf",
    vendor_proposal_2_url: str = "https://rfxagentichub9781132764.blob.core.windows.net/71693736-86ed-47c3-8342-4ce83deff0c6-azureml-blobstore/UI/2025-06-26_153459_UTC/Vendor_Proposals/SecureNet/",
    industry: str = "technology",
    rfp_type: str = "enterprise_network"
) -> dict:
    """
    Hybrid MCP implementation for Enterprise Network RFP with document parsing
    
    Args:
        rfp_document_url: URL to the Enterprise Network RFP document
        vendor_proposal_1_url: URL to Cyberguard vendor proposal
        vendor_proposal_2_url: URL to SecureNet vendor proposal
        industry: Industry sector (defaults to "technology")
        rfp_type: Type of RFP (defaults to "enterprise_network")
    
    Returns:
        dict: Industry context from Azure MCP or local fallback with document analysis
    """
    
    # Parse documents first
    document_analysis = _parse_rfp_documents(rfp_document_url, vendor_proposal_1_url, vendor_proposal_2_url)
    
    # Try Azure MCP first with document context
    try:
        azure_result = _get_azure_mcp_context_with_docs(industry, rfp_type, document_analysis)
        if azure_result["status"] == "success":
            return azure_result
    except Exception as azure_error:
        print(f"Azure MCP failed: {azure_error}")
    
    # Fallback to local simulation with document analysis
    try:
        local_result = _get_local_knowledge_context_with_docs(industry, rfp_type, document_analysis)
        local_result["status"] = "fallback"
        local_result["source"] = "local_simulation"
        local_result["note"] = "Azure MCP unavailable, using local knowledge base with document analysis"
        return local_result
    except Exception as local_error:
        return {
            "status": "error",
            "error": f"Both Azure MCP and local fallback failed: {local_error}",
            "industry": industry,
            "rfp_type": rfp_type,
            "document_analysis": document_analysis
        }

def _parse_rfp_documents(rfp_url: str, vendor1_url: str, vendor2_url: str) -> dict:
    """
    Parse RFP and vendor proposal documents from Azure Blob Storage
    """
    
    document_analysis = {
        "rfp_content": "",
        "vendor_proposals": {},
        "parsing_status": {},
        "key_requirements": [],
        "vendor_capabilities": {}
    }
    
    # Parse RFP Document
    try:
        rfp_content = _download_and_parse_pdf(rfp_url)
        document_analysis["rfp_content"] = rfp_content
        document_analysis["parsing_status"]["rfp"] = "success"
        
        # Extract key requirements from RFP
        document_analysis["key_requirements"] = _extract_network_requirements(rfp_content)
        
    except Exception as e:
        document_analysis["parsing_status"]["rfp"] = f"failed: {str(e)}"
        document_analysis["rfp_content"] = "Failed to parse RFP document"
    
    # Parse Cyberguard Proposal
    try:
        cyberguard_content = _download_and_parse_pdf(vendor1_url)
        document_analysis["vendor_proposals"]["Cyberguard"] = cyberguard_content
        document_analysis["parsing_status"]["cyberguard"] = "success"
        
        # Extract vendor capabilities
        document_analysis["vendor_capabilities"]["Cyberguard"] = _extract_vendor_capabilities(cyberguard_content, "Cyberguard")
        
    except Exception as e:
        document_analysis["parsing_status"]["cyberguard"] = f"failed: {str(e)}"
        document_analysis["vendor_proposals"]["Cyberguard"] = "Failed to parse Cyberguard proposal"
    
    # Parse SecureNet Proposal (handle directory URL)
    try:
        if vendor2_url.endswith('/'):
            # This is a directory, try common document names
            securenet_content = _parse_directory_documents(vendor2_url)
        else:
            securenet_content = _download_and_parse_pdf(vendor2_url)
            
        document_analysis["vendor_proposals"]["SecureNet"] = securenet_content
        document_analysis["parsing_status"]["securenet"] = "success"
        
        # Extract vendor capabilities
        document_analysis["vendor_capabilities"]["SecureNet"] = _extract_vendor_capabilities(securenet_content, "SecureNet")
        
    except Exception as e:
        document_analysis["parsing_status"]["securenet"] = f"failed: {str(e)}"
        document_analysis["vendor_proposals"]["SecureNet"] = "Failed to parse SecureNet proposal"
    
    return document_analysis

def _download_and_parse_pdf(url: str) -> str:
    """Download and parse PDF content from Azure Blob Storage"""
    
    try:
        # Download PDF
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse PDF content
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        return text_content.strip()
        
    except Exception as e:
        raise Exception(f"Failed to download/parse PDF from {url}: {str(e)}")

def _parse_directory_documents(directory_url: str) -> str:
    """Parse documents from a directory URL (for SecureNet)"""
    
    # Try common document names in the directory
    common_names = [
        "proposal.pdf",
        "response.pdf", 
        "securenet_proposal.pdf",
        "securenet_response.pdf",
        "network_proposal.pdf"
    ]
    
    content = ""
    for doc_name in common_names:
        try:
            doc_url = directory_url + doc_name
            doc_content = _download_and_parse_pdf(doc_url)
            content += f"\n=== {doc_name} ===\n{doc_content}"
        except:
            continue
    
    if not content:
        # If no standard documents found, return directory info
        content = f"SecureNet proposal directory accessed but no standard documents found at {directory_url}"
    
    return content

def _extract_network_requirements(rfp_content: str) -> list:
    """Extract key network requirements from RFP content"""
    
    requirements = []
    content_lower = rfp_content.lower()
    
    # Network infrastructure requirements
    if "bandwidth" in content_lower:
        requirements.append("Bandwidth requirements specified")
    if "security" in content_lower:
        requirements.append("Network security requirements")
    if "redundancy" in content_lower or "failover" in content_lower:
        requirements.append("Redundancy and failover capabilities")
    if "monitoring" in content_lower:
        requirements.append("Network monitoring and management")
    if "firewall" in content_lower:
        requirements.append("Firewall and perimeter security")
    if "vpn" in content_lower:
        requirements.append("VPN connectivity requirements")
    if "wifi" in content_lower or "wireless" in content_lower:
        requirements.append("Wireless network capabilities")
    if "switch" in content_lower:
        requirements.append("Network switching infrastructure")
    if "router" in content_lower:
        requirements.append("Routing infrastructure")
    if "compliance" in content_lower:
        requirements.append("Compliance and regulatory requirements")
    
    # Add default requirements if none found
    if not requirements:
        requirements = [
            "Enterprise network infrastructure",
            "Security and compliance",
            "Performance and reliability",
            "Management and monitoring"
        ]
    
    return requirements

def _extract_vendor_capabilities(proposal_content: str, vendor_name: str) -> dict:
    """Extract vendor capabilities from proposal content"""
    
    capabilities = {
        "vendor_name": vendor_name,
        "technical_capabilities": [],
        "security_features": [],
        "management_tools": [],
        "compliance_certifications": [],
        "performance_specs": {},
        "support_services": []
    }
    
    content_lower = proposal_content.lower()
    
    # Technical capabilities
    if "switch" in content_lower:
        capabilities["technical_capabilities"].append("Network switching")
    if "router" in content_lower:
        capabilities["technical_capabilities"].append("Routing solutions")
    if "firewall" in content_lower:
        capabilities["technical_capabilities"].append("Firewall systems")
    if "wireless" in content_lower or "wifi" in content_lower:
        capabilities["technical_capabilities"].append("Wireless networking")
    if "cloud" in content_lower:
        capabilities["technical_capabilities"].append("Cloud integration")
    
    # Security features
    if "encryption" in content_lower:
        capabilities["security_features"].append("Data encryption")
    if "intrusion" in content_lower:
        capabilities["security_features"].append("Intrusion detection/prevention")
    if "authentication" in content_lower:
        capabilities["security_features"].append("Authentication systems")
    if "vpn" in content_lower:
        capabilities["security_features"].append("VPN capabilities")
    
    # Management tools
    if "monitoring" in content_lower:
        capabilities["management_tools"].append("Network monitoring")
    if "dashboard" in content_lower:
        capabilities["management_tools"].append("Management dashboard")
    if "analytics" in content_lower:
        capabilities["management_tools"].append("Network analytics")
    
    # Compliance
    if "iso" in content_lower:
        capabilities["compliance_certifications"].append("ISO certifications")
    if "sox" in content_lower:
        capabilities["compliance_certifications"].append("SOX compliance")
    if "hipaa" in content_lower:
        capabilities["compliance_certifications"].append("HIPAA compliance")
    
    # Support services
    if "24/7" in content_lower or "24x7" in content_lower:
        capabilities["support_services"].append("24/7 support")
    if "training" in content_lower:
        capabilities["support_services"].append("Training services")
    if "maintenance" in content_lower:
        capabilities["support_services"].append("Maintenance services")
    
    return capabilities

def _get_azure_mcp_context_with_docs(industry: str, rfp_type: str, document_analysis: dict) -> dict:
    """
    Get industry context using Azure MCP with document analysis
    """
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        
        # Initialize Azure AI Project Client
        project_client = AIProjectClient(
            endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
            credential=DefaultAzureCredential()
        )
        
        # Create specialized agent for Enterprise Network RFP
        agent = project_client.agents.create_agent(
            model="gpt-4",
            name="Enterprise Network MCP Agent",
            description="Specialized in enterprise network infrastructure analysis and vendor evaluation",
            instructions=f"""
            You are an expert in enterprise network infrastructure for the {industry} sector.
            Use MCP tools to retrieve current industry standards for enterprise networking.
            Focus on network security, performance, scalability, and management requirements.
            Provide comprehensive analysis based on the actual RFP and vendor proposals provided.
            """,
            tools=[
                {
                    "type": "mcp",
                    "mcp": {
                        "server_url": os.getenv("INDUSTRY_MCP_SERVER_URL", "https://mcp-foundry.azurewebsites.net"),
                        "server_label": "enterprise_network_standards",
                        "require_approval": {
                            "never": [
                                "get_network_standards",
                                "get_security_requirements",
                                "get_performance_benchmarks",
                                "get_vendor_evaluation_criteria"
                            ]
                        }
                    }
                }
            ]
        )
        
        # Create comprehensive query with document context
        rfp_summary = document_analysis["rfp_content"][:1000] if document_analysis["rfp_content"] else "RFP content not available"
        requirements = document_analysis.get("key_requirements", [])
        vendor_caps = document_analysis.get("vendor_capabilities", {})
        
        query_content = f"""
        **ENTERPRISE NETWORK RFP ANALYSIS REQUEST**
        
        **RFP Type:** {rfp_type}
        **Industry:** {industry}
        
        **RFP Summary:**
        {rfp_summary}
        
        **Identified Requirements:**
        {chr(10).join([f"- {req}" for req in requirements])}
        
        **Vendor Proposals:**
        - Cyberguard: {len(vendor_caps.get('Cyberguard', {}).get('technical_capabilities', []))} technical capabilities identified
        - SecureNet: {len(vendor_caps.get('SecureNet', {}).get('technical_capabilities', []))} technical capabilities identified
        
        **Please use MCP tools to provide:**
        
        1. **Enterprise Network Industry Standards**
           - Network infrastructure evaluation criteria with weights
           - Security requirements and compliance frameworks
           - Performance benchmarks (bandwidth, latency, uptime)
           - Scalability and redundancy standards
        
        2. **Vendor Evaluation Framework**
           - Technical capability assessment criteria
           - Security posture evaluation methods
           - Financial stability requirements
           - Support and maintenance standards
        
        3. **Risk Assessment Guidelines**
           - Common enterprise network risks
           - Vendor-specific risk factors
           - Mitigation strategies and best practices
        
        4. **Implementation Considerations**
           - Typical deployment timelines
           - Change management requirements
           - Integration complexity factors
           - Success metrics and KPIs
        
        **Format as structured JSON with:**
        - scorecard_parameters (with weights)
        - industry_benchmarks
        - compliance_requirements  
        - risk_factors
        - evaluation_criteria
        - implementation_guidelines
        
        Include confidence scores and reference current industry standards.
        """
        
        # Execute MCP query
        thread = project_client.agents.create_thread()
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=query_content
        )
        
        run = project_client.agents.create_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Poll for completion
        import time
        max_wait = 90  # Extended timeout for complex analysis
        wait_time = 0
        
        while run.status in ["queued", "in_progress", "requires_action"] and wait_time < max_wait:
            time.sleep(3)
            wait_time += 3
            run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        
        if wait_time >= max_wait:
            raise Exception("Azure MCP agent timeout")
        
        if run.status == "failed":
            raise Exception(f"Azure MCP agent failed: {run.last_error}")
        
        # Get response
        messages = project_client.agents.list_messages(thread_id=thread.id)
        if not messages.data:
            raise Exception("No response from Azure MCP agent")
        
        response_content = messages.data[0].content[0].text.value
        
        # Parse response
        try:
            parsed_response = json.loads(response_content)
        except:
            parsed_response = {
                "raw_response": response_content,
                "parsed": False
            }
        
        return {
            "status": "success",
            "source": "azure_mcp",
            "industry": industry,
            "rfp_type": rfp_type,
            "context": parsed_response,
            "document_analysis": document_analysis,
            "metadata": {
                "agent_id": agent.id,
                "thread_id": thread.id,
                "mcp_server": os.getenv("INDUSTRY_MCP_SERVER_URL", "default"),
                "response_time": wait_time,
                "confidence": "high",
                "documents_parsed": len([k for k, v in document_analysis["parsing_status"].items() if "success" in str(v)])
            },
            "recommendations": _extract_recommendations_from_mcp(parsed_response)
        }
        
    except ImportError:
        raise Exception("Azure AI Projects SDK not available")
    except Exception as e:
        raise Exception(f"Azure MCP error: {str(e)}")

def _get_local_knowledge_context_with_docs(industry: str, rfp_type: str, document_analysis: dict) -> dict:
    """
    Enhanced local knowledge base for Enterprise Network RFP with document analysis
    """
    
    # Enterprise Network specific knowledge base
    enterprise_network_knowledge = {
        "enterprise_network": {
            "scorecard_parameters": [
                {"criteria": "Network Security & Firewall", "weight": 25, "description": "Perimeter security, intrusion prevention, threat detection"},
                {"criteria": "Infrastructure Scalability", "weight": 20, "description": "Capacity planning, growth accommodation, performance under load"},
                {"criteria": "Redundancy & Reliability", "weight": 18, "description": "Failover capabilities, uptime guarantees, disaster recovery"},
                {"criteria": "Management & Monitoring", "weight": 15, "description": "Network visibility, analytics, automated management tools"},
                {"criteria": "Compliance & Governance", "weight": 12, "description": "Regulatory compliance, audit capabilities, policy enforcement"},
                {"criteria": "Integration Capabilities", "weight": 10, "description": "Legacy system integration, cloud connectivity, API support"}
            ],
            "industry_benchmarks": {
                "uptime_sla": "99.99% (52.56 minutes downtime/year)",
                "network_latency": "< 5ms for critical applications",
                "throughput_capacity": "10Gbps minimum backbone with 100Gbps capability", 
                "security_standards": ["ISO 27001", "NIST Cybersecurity Framework", "Zero Trust Architecture"],
                "failover_time": "< 30 seconds for automatic failover",
                "monitoring_coverage": "100% network visibility with real-time alerting"
            },
            "compliance_requirements": [
                "Network segmentation and micro-segmentation",
                "Encrypted communications (TLS 1.3 minimum)",
                "Multi-factor authentication for network access",
                "Comprehensive audit logging and SIEM integration",
                "Regular penetration testing and vulnerability assessments",
                "Incident response and business continuity planning"
            ],
            "risk_factors": [
                "Single points of failure in network design",
                "Inadequate redundancy and backup systems",
                "Insufficient security monitoring and threat detection",
                "Vendor lock-in and proprietary protocols",
                "Complex integration with existing infrastructure",
                "Inadequate documentation and knowledge transfer"
            ],
            "evaluation_criteria": {
                "technical_assessment": [
                    "Network architecture design and documentation",
                    "Security implementation and threat mitigation",
                    "Performance testing and capacity planning",
                    "Redundancy and disaster recovery capabilities"
                ],
                "vendor_assessment": [
                    "Industry experience and track record",
                    "Financial stability and company viability",
                    "Support organization and response times",
                    "Training and knowledge transfer programs"
                ],
                "commercial_assessment": [
                    "Total cost of ownership analysis",
                    "Licensing and subscription models",
                    "Implementation and professional services costs",
                    "Ongoing maintenance and support fees"
                ]
            },
            "implementation_guidelines": {
                "phase_1": "Design validation and pilot deployment (2-3 months)",
                "phase_2": "Core infrastructure deployment (3-6 months)", 
                "phase_3": "Full rollout and optimization (6-12 months)",
                "critical_success_factors": [
                    "Executive sponsorship and change management",
                    "Comprehensive testing in non-production environment",
                    "Detailed cutover planning and rollback procedures",
                    "Staff training and certification programs"
                ]
            }
        }
    }
    
    # Get context data
    context_data = enterprise_network_knowledge["enterprise_network"]
    
    # Enhance with document analysis
    enhanced_context = context_data.copy()
    
    # Add document-specific insights
    if document_analysis["key_requirements"]:
        enhanced_context["rfp_specific_requirements"] = document_analysis["key_requirements"]
    
    if document_analysis["vendor_capabilities"]:
        enhanced_context["vendor_analysis"] = {
            "cyberguard_capabilities": document_analysis["vendor_capabilities"].get("Cyberguard", {}),
            "securenet_capabilities": document_analysis["vendor_capabilities"].get("SecureNet", {}),
            "capability_comparison": _compare_vendor_capabilities(document_analysis["vendor_capabilities"])
        }
    
    # Generate document-informed recommendations
    doc_recommendations = _generate_document_recommendations(document_analysis)
    
    return {
        "status": "success",
        "industry": industry,
        "rfp_type": rfp_type,
        "context": enhanced_context,
        "document_analysis": document_analysis,
        "metadata": {
            "confidence_score": 0.85,  # High confidence with document analysis
            "last_updated": "2024-Q4",
            "documents_analyzed": len([k for k, v in document_analysis["parsing_status"].items() if "success" in str(v)]),
            "analysis_type": "document_enhanced_local_knowledge"
        },
        "recommendations": doc_recommendations
    }

def _compare_vendor_capabilities(vendor_capabilities: dict) -> dict:
    """Compare capabilities between vendors"""
    
    comparison = {
        "technical_capabilities": {},
        "security_features": {},
        "support_services": {},
        "advantage_analysis": {}
    }
    
    vendors = ["Cyberguard", "SecureNet"]
    
    for vendor in vendors:
        if vendor in vendor_capabilities:
            caps = vendor_capabilities[vendor]
            comparison["technical_capabilities"][vendor] = len(caps.get("technical_capabilities", []))
            comparison["security_features"][vendor] = len(caps.get("security_features", []))
            comparison["support_services"][vendor] = len(caps.get("support_services", []))
    
    # Determine advantages
    for category in ["technical_capabilities", "security_features", "support_services"]:
        if category in comparison:
            scores = comparison[category]
            if scores:
                leader = max(scores.items(), key=lambda x: x[1])
                comparison["advantage_analysis"][category] = f"{leader[0]} leads with {leader[1]} capabilities"
    
    return comparison

def _generate_document_recommendations(document_analysis: dict) -> list:
    """Generate recommendations based on document analysis"""
    
    recommendations = []
    
    # RFP-based recommendations
    requirements = document_analysis.get("key_requirements", [])
    if "security" in str(requirements).lower():
        recommendations.append("Prioritize vendors with strong security capabilities based on RFP requirements")
    
    if "monitoring" in str(requirements).lower():
        recommendations.append("Evaluate network monitoring and management tools thoroughly")
    
    if "redundancy" in str(requirements).lower():
        recommendations.append("Assess failover and redundancy capabilities in detail")
    
    # Vendor-based recommendations
    vendor_caps = document_analysis.get("vendor_capabilities", {})
    
    if "Cyberguard" in vendor_caps and "SecureNet" in vendor_caps:
        recommendations.append("Conduct side-by-side comparison of Cyberguard and SecureNet capabilities")
        recommendations.append("Request proof of concept from both vendors for critical requirements")
    
    # Parsing status recommendations
    parsing_status = document_analysis.get("parsing_status", {})
    failed_parsing = [k for k, v in parsing_status.items() if "failed" in str(v)]
    
    if failed_parsing:
        recommendations.append(f"Request alternative document formats for {', '.join(failed_parsing)} due to parsing issues")
    
    # Default recommendations
    if not recommendations:
        recommendations = [
            "Focus on enterprise network security and compliance requirements",
            "Evaluate scalability and performance under peak loads",
            "Assess vendor support capabilities and response times",
            "Validate integration with existing infrastructure"
        ]
    
    return recommendations

def _extract_recommendations_from_mcp(mcp_response: Dict[str, Any]) -> list:
    """Extract actionable recommendations from MCP response"""
    
    recommendations = []
    
    # Extract from structured response
    if isinstance(mcp_response, dict):
        # Look for recommendations in various fields
        for key in ["recommendations", "best_practices", "key_insights", "evaluation_criteria"]:
            if key in mcp_response:
                if isinstance(mcp_response[key], list):
                    recommendations.extend(mcp_response[key])
                elif isinstance(mcp_response[key], str):
                    recommendations.append(mcp_response[key])
    
    # Enterprise network specific recommendations
    if not recommendations:
        recommendations = [
            "Evaluate network security architecture and threat detection capabilities",
            "Assess scalability and performance under enterprise workloads",
            "Validate redundancy, failover, and disaster recovery capabilities",
            "Review management tools and network visibility features",
            "Verify compliance with industry security standards",
            "Conduct thorough vendor financial and technical due diligence"
        ]
    
    return recommendations[:8]  # Limit to top 8 recommendations

def _get_azure_mcp_context(industry: str, rfp_type: str, rfp_content: str) -> dict:
    """
    Get industry context using Azure AI Foundry's native MCP support
    """
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        import asyncio
        
        # Initialize Azure AI Project Client
        project_client = AIProjectClient(
            endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
            credential=DefaultAzureCredential()
        )
        
        # Create Azure AI Agent with MCP tools
        agent = project_client.agents.create_agent(
            model="gpt-4",  # Your deployed model name
            name="Industry Context MCP Agent",
            description="Provides industry-specific context and benchmarks via MCP",
            instructions=f"""
            You are an industry analysis expert for the {industry} sector.
            Use MCP tools to retrieve current industry standards, benchmarks, and compliance requirements.
            Provide comprehensive analysis including scorecard parameters, performance benchmarks, 
            regulatory requirements, and market insights.
            """,
            tools=[
                {
                    "type": "mcp",
                    "mcp": {
                        # Use Azure AI Foundry's MCP server or your custom one
                        "server_url": os.getenv("INDUSTRY_MCP_SERVER_URL", "https://mcp-foundry.azurewebsites.net"),
                        "server_label": "industry_benchmarks",
                        "require_approval": {
                            "never": [
                                "get_industry_standards",
                                "get_compliance_requirements", 
                                "get_market_benchmarks"
                            ]
                        }
                    }
                }
            ]
        )
        
        # Create thread for conversation
        thread = project_client.agents.create_thread()
        
        # Create comprehensive query
        query_content = f"""
        Please provide comprehensive industry context for:
        
        **Industry:** {industry}
        **RFP Type:** {rfp_type}
        **RFP Summary:** {rfp_content[:300] if rfp_content else "Not provided"}
        
        Use MCP tools to retrieve and provide:
        
        1. **Industry-Standard Scorecard Parameters**
           - Evaluation criteria with recommended weightings
           - Key performance indicators
           - Decision factors specific to {industry} sector
        
        2. **Regulatory & Compliance Requirements**
           - Mandatory compliance frameworks
           - Industry certifications required
           - Data protection and security standards
        
        3. **Performance Benchmarks & SLAs**
           - Industry-standard performance metrics
           - Typical SLA requirements
           - Availability and reliability expectations
        
        4. **Market Insights & Risk Factors**
           - Implementation timelines and costs
           - Common risk factors and mitigation strategies
           - Success factors and best practices
        
        5. **Vendor Evaluation Criteria**
           - Industry-specific evaluation frameworks
           - Red flags and warning signs
           - Reference check requirements
        
        Format the response as structured JSON with clear sections for each area.
        Include confidence scores and data source information where available.
        """
        
        # Send message to agent
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=query_content
        )
        
        # Execute agent with MCP tools
        run = project_client.agents.create_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Poll for completion (with timeout)
        import time
        max_wait = 60  # 60 seconds timeout
        wait_time = 0
        
        while run.status in ["queued", "in_progress", "requires_action"] and wait_time < max_wait:
            time.sleep(2)
            wait_time += 2
            run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        
        if wait_time >= max_wait:
            raise Exception("Azure MCP agent timeout")
        
        if run.status == "failed":
            raise Exception(f"Azure MCP agent failed: {run.last_error}")
        
        # Get response
        messages = project_client.agents.list_messages(thread_id=thread.id)
        if not messages.data:
            raise Exception("No response from Azure MCP agent")
        
        response_content = messages.data[0].content[0].text.value
        
        # Try to parse as JSON, fallback to text
        try:
            parsed_response = json.loads(response_content)
        except:
            parsed_response = {"raw_response": response_content}
        
        return {
            "status": "success",
            "source": "azure_mcp",
            "industry": industry,
            "rfp_type": rfp_type,
            "context": parsed_response,
            "metadata": {
                "agent_id": agent.id,
                "thread_id": thread.id,
                "mcp_server": os.getenv("INDUSTRY_MCP_SERVER_URL", "default"),
                "response_time": wait_time,
                "confidence": "high"
            },
            "recommendations": _extract_recommendations_from_mcp(parsed_response)
        }
        
    except ImportError:
        raise Exception("Azure AI Projects SDK not available")
    except Exception as e:
        raise Exception(f"Azure MCP error: {str(e)}")

def _get_local_knowledge_context(industry: str, rfp_type: str) -> dict:
    """
    Fallback to local embedded knowledge base
    """
    
    # Embedded industry knowledge base (same as original implementation)
    industry_knowledge = {
        "technology": {
            "software": {
                "scorecard_parameters": [
                    {"criteria": "Technical Architecture", "weight": 25, "description": "System design, scalability, modularity"},
                    {"criteria": "Security & Compliance", "weight": 20, "description": "Data protection, access controls, audit trails"},
                    {"criteria": "Integration Capabilities", "weight": 15, "description": "API quality, data exchange, interoperability"},
                    {"criteria": "Performance & Scalability", "weight": 15, "description": "Response times, throughput, load handling"},
                    {"criteria": "User Experience", "weight": 10, "description": "Interface design, usability, accessibility"},
                    {"criteria": "Support & Maintenance", "weight": 10, "description": "Documentation, training, ongoing support"},
                    {"criteria": "Total Cost of Ownership", "weight": 5, "description": "Licensing, implementation, operational costs"}
                ],
                "industry_benchmarks": {
                    "response_time_sla": "< 2 seconds for 95% of requests",
                    "uptime_requirement": "99.9% (8.76 hours downtime/year)",
                    "security_standards": ["SOC 2 Type II", "ISO 27001", "GDPR compliance"],
                    "integration_protocols": ["REST API", "GraphQL", "Webhooks", "SOAP"],
                    "scalability_metrics": "Handle 10x current load without degradation",
                    "support_levels": "24/7 critical, 4h response time"
                },
                "compliance_requirements": [
                    "Data encryption at rest and in transit",
                    "Role-based access controls",
                    "Audit logging for all data access",
                    "Regular security assessments",
                    "Incident response procedures"
                ],
                "market_insights": {
                    "average_implementation_time": "3-6 months",
                    "typical_budget_range": "$100K - $1M",
                    "success_factors": ["Executive sponsorship", "Change management", "Data quality"],
                    "common_risks": ["Scope creep", "Integration complexity", "User adoption"]
                }
            },
            "infrastructure": {
                "scorecard_parameters": [
                    {"criteria": "Technical Specifications", "weight": 30, "description": "Hardware specs, performance capacity"},
                    {"criteria": "Reliability & Availability", "weight": 25, "description": "Uptime guarantees, redundancy"},
                    {"criteria": "Security Features", "weight": 20, "description": "Physical security, network protection"},
                    {"criteria": "Scalability & Flexibility", "weight": 15, "description": "Growth capacity, adaptability"},
                    {"criteria": "Cost Efficiency", "weight": 10, "description": "Price per unit, operational costs"}
                ],
                "industry_benchmarks": {
                    "uptime_sla": "99.99% (52.56 minutes downtime/year)",
                    "performance_standards": "Sub-millisecond latency",
                    "capacity_planning": "20% overhead for growth",
                    "security_requirements": ["Physical access controls", "Network segmentation", "Monitoring"]
                }
            }
        },
        "financial_services": {
            "software": {
                "scorecard_parameters": [
                    {"criteria": "Regulatory Compliance", "weight": 30, "description": "SOX, PCI DSS, Basel III compliance"},
                    {"criteria": "Security & Risk Management", "weight": 25, "description": "Fraud detection, data protection"},
                    {"criteria": "Audit Trail & Reporting", "weight": 15, "description": "Transaction logging, regulatory reports"},
                    {"criteria": "Performance & Reliability", "weight": 15, "description": "High availability, disaster recovery"},
                    {"criteria": "Integration Capabilities", "weight": 10, "description": "Core banking, payment systems"},
                    {"criteria": "Cost & ROI", "weight": 5, "description": "Implementation and operational costs"}
                ],
                "industry_benchmarks": {
                    "transaction_processing": "< 100ms per transaction",
                    "data_retention": "7-10 years minimum",
                    "audit_requirements": "Real-time monitoring, quarterly reviews",
                    "security_standards": ["PCI DSS Level 1", "SOX compliance", "ISO 27001"],
                    "availability_sla": "99.99% during business hours"
                },
                "compliance_requirements": [
                    "SOX Section 404 controls",
                    "PCI DSS for payment data",
                    "GDPR for customer data",
                    "Anti-money laundering (AML)",
                    "Know Your Customer (KYC)"
                ]
            }
        },
        "healthcare": {
            "software": {
                "scorecard_parameters": [
                    {"criteria": "HIPAA Compliance", "weight": 35, "description": "Patient data protection, access controls"},
                    {"criteria": "Clinical Workflow", "weight": 25, "description": "EHR integration, clinical decision support"},
                    {"criteria": "Interoperability", "weight": 20, "description": "HL7 FHIR, data exchange standards"},
                    {"criteria": "Usability & Training", "weight": 10, "description": "Clinician adoption, training requirements"},
                    {"criteria": "Performance & Reliability", "weight": 10, "description": "System availability, response times"}
                ],
                "industry_benchmarks": {
                    "hipaa_requirements": "Encryption, access logs, breach notification",
                    "interoperability_standards": ["HL7 FHIR R4", "DICOM", "IHE profiles"],
                    "clinical_performance": "< 3 second response for critical queries",
                    "availability_sla": "99.9% with 4-hour maintenance windows"
                }
            }
        }
    }
    
    # Get industry-specific data
    industry_lower = industry.lower()
    rfp_type_lower = rfp_type.lower()
    
    if industry_lower in industry_knowledge:
        industry_data = industry_knowledge[industry_lower]
        
        # Try to find specific RFP type, fallback to first available
        if rfp_type_lower in industry_data:
            context_data = industry_data[rfp_type_lower]
        else:
            context_data = list(industry_data.values())[0]
        
        return {
            "status": "success",
            "industry": industry,
            "rfp_type": rfp_type,
            "context": {
                "scorecard_parameters": context_data["scorecard_parameters"],
                "industry_benchmarks": context_data["industry_benchmarks"],
                "compliance_requirements": context_data.get("compliance_requirements", []),
                "market_insights": context_data.get("market_insights", {}),
                "confidence_score": 0.75,  # Lower confidence for local data
                "last_updated": "2024-Q4"
            },
            "recommendations": [
                f"Ensure all vendors meet {industry} industry standards",
                f"Prioritize {context_data['scorecard_parameters'][0]['criteria']} (highest weight)",
                "Validate compliance with all regulatory requirements",
                "Consider implementation timeline and change management"
            ]
        }
    else:
        # Generic fallback
        return {
            "status": "partial",
            "industry": industry,
            "rfp_type": rfp_type,
            "context": {
                "scorecard_parameters": [
                    {"criteria": "Technical Capability", "weight": 30, "description": "Core functionality and features"},
                    {"criteria": "Vendor Reliability", "weight": 25, "description": "Company stability and track record"},
                    {"criteria": "Cost Effectiveness", "weight": 20, "description": "Total cost of ownership"},
                    {"criteria": "Implementation Approach", "weight": 15, "description": "Project methodology and timeline"},
                    {"criteria": "Support & Maintenance", "weight": 10, "description": "Ongoing support quality"}
                ],
                "industry_benchmarks": {
                    "general_requirements": "Standard commercial practices",
                    "performance_expectations": "Meet stated requirements",
                    "support_standards": "Business hour support minimum"
                },
                "compliance_requirements": ["Standard data protection", "Basic security measures"],
                "confidence_score": 0.60,
                "last_updated": "2024-Q4"
            },
            "recommendations": [
                "Industry-specific data not available - using general framework",
                "Consider consulting industry experts for specialized requirements",
                "Validate requirements against industry best practices"
            ]
        }

def _extract_recommendations_from_mcp(mcp_response: Dict[str, Any]) -> list:
    """Extract actionable recommendations from MCP response"""
    
    recommendations = []
    
    # Extract from structured response
    if isinstance(mcp_response, dict):
        # Look for recommendations in various fields
        for key in ["recommendations", "best_practices", "key_insights"]:
            if key in mcp_response:
                if isinstance(mcp_response[key], list):
                    recommendations.extend(mcp_response[key])
                elif isinstance(mcp_response[key], str):
                    recommendations.append(mcp_response[key])
    
    # Default recommendations if none found
    if not recommendations:
        recommendations = [
            "Follow industry-standard evaluation criteria",
            "Ensure regulatory compliance requirements are met",
            "Validate vendor capabilities against performance benchmarks",
            "Conduct thorough reference checks"
        ]
    
    return recommendations[:5]  # Limit to top 5 recommendations