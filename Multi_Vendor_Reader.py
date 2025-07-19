from promptflow import tool
import requests
import PyPDF2
import io
from xml.etree import ElementTree as ET
import json

@tool
def Multi_Vendor_Reader(vendor_proposal_1: str, vendor_proposal_2: str) -> str:
    """
    Single vendor reader that processes both Cyberguard and SecureNet proposals
    
    Args:
        vendor_proposal_1: Cyberguard vendor folder path
        vendor_proposal_2: SecureNet vendor folder path
    
    Returns:
        JSON string with both vendors' data ready for Sxoring_Engine
    """
    
    # Define expected vendor configuration
    VENDOR_CONFIG = {
        "cyberguard": {
            "expected_path": "https://rfxagentichub9781132764.blob.core.windows.net/71693736-86ed-47c3-8342-4ce83deff0c6-azureml-blobstore/UI/2025-06-26_153459_UTC/Vendor_Proposals/Cyberguard%20/",
            "vendor_type": "Security-focused provider",
            "expected_files": [
                "cyberguard_solution.pdf",
                "security_framework.pdf", 
                "cybersecurity_proposal.pdf",
                "technical_proposal.pdf",
                "commercial_proposal.pdf",
                "company_qualifications.pdf"
            ]
        },
        "securenet": {
            "expected_path": "https://rfxagentichub9781132764.blob.core.windows.net/71693736-86ed-47c3-8342-4ce83deff0c6-azureml-blobstore/UI/2025-06-26_153459_UTC/Vendor_Proposals/SecureNet/",
            "vendor_type": "Network security specialist",
            "expected_files": [
                "securenet_proposal.pdf",
                "network_security_proposal.pdf",
                "network_architecture.pdf",
                "technical_proposal.pdf",
                "commercial_proposal.pdf",
                "company_qualifications.pdf"
            ]
        }
    }
    
    def identify_vendor_from_path(folder_path: str) -> tuple:
        """Identify which vendor this path represents"""
        if not folder_path:
            return "Unknown", False, "unknown"
            
        # Check for exact matches
        if folder_path == VENDOR_CONFIG["cyberguard"]["expected_path"]:
            return "Cyberguard", True, "cyberguard"
        elif folder_path == VENDOR_CONFIG["securenet"]["expected_path"]:
            return "SecureNet", True, "securenet"
        
        # Check for partial matches
        if "Cyberguard%20" in folder_path or "cyberguard" in folder_path.lower():
            exact_match = folder_path == VENDOR_CONFIG["cyberguard"]["expected_path"]
            return "Cyberguard", exact_match, "cyberguard"
        elif "SecureNet" in folder_path or "securenet" in folder_path.lower():
            exact_match = folder_path == VENDOR_CONFIG["securenet"]["expected_path"]
            return "SecureNet", exact_match, "securenet"
        
        # Fallback extraction
        path_parts = folder_path.rstrip('/').split('/')
        for part in reversed(path_parts):
            if part and part != 'Vendor_Proposals':
                vendor_name = part.replace('%20', ' ').replace('_', ' ').replace('-', ' ').strip()
                return vendor_name.title() if vendor_name else "Unknown", False, "unknown"
        
        return "Unknown", False, "unknown"
    
    def read_pdf_from_uri(blob_uri: str) -> str:
        """Read PDF content from Azure Blob Storage URI"""
        try:
            response = requests.get(blob_uri, timeout=60)
            
            if response.status_code == 200:
                pdf_file = io.BytesIO(response.content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text_content = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text_content += extracted_text + "\n"
                
                return text_content.strip() if text_content.strip() else None
            elif response.status_code == 404:
                return None
            else:
                return None
                
        except Exception as e:
            return None
    
    def read_svg_from_uri(blob_uri: str) -> str:
        """Read SVG content from Azure Blob Storage URI"""
        try:
            response = requests.get(blob_uri, timeout=60)
            
            if response.status_code == 200:
                try:
                    root = ET.fromstring(response.content)
                    text_elements = (root.findall('.//text') or 
                                   root.findall('.//{http://www.w3.org/2000/svg}text'))
                    
                    svg_text = " ".join([elem.text for elem in text_elements if elem.text and elem.text.strip()])
                    
                    if svg_text.strip():
                        return f"SVG Content: {svg_text.strip()}"
                    else:
                        return f"SVG diagram: {blob_uri.split('/')[-1]}"
                        
                except ET.ParseError:
                    return f"SVG file: {blob_uri.split('/')[-1]}"
            else:
                return None
                
        except Exception as e:
            return None
    
    def extract_technical_features(vendor_text: str, vendor_name: str) -> dict:
        """Extract technical features from vendor text"""
        text_lower = vendor_text.lower()
        
        return {
            "solution_architecture": {
                "architecture_provided": any(word in text_lower for word in ['architecture', 'design', 'solution']),
                "scalable_design": "scalable" in text_lower or "scale" in text_lower,
                "integration_capabilities": "integration" in text_lower or "api" in text_lower,
                "technology_stack": "technology" in text_lower or "stack" in text_lower
            },
            "security_compliance": {
                "certifications": [kw.upper() for kw in ['iso27001', 'soc2', 'pci', 'gdpr'] if kw in text_lower],
                "encryption_support": "encryption" in text_lower,
                "compliance_framework": "compliance" in text_lower
            },
            "performance_sla": {
                "uptime_sla": "99.9%" if "99.9" in vendor_text else "99%" if "99" in vendor_text else "N/A",
                "response_time": "< 100ms" if "100ms" in text_lower else "< 200ms" if "200ms" in text_lower else "N/A",
                "performance_monitoring": "monitoring" in text_lower
            },
            "scalability": {
                "horizontal_scaling": "horizontal" in text_lower and "scal" in text_lower,
                "vertical_scaling": "vertical" in text_lower and "scal" in text_lower,
                "auto_scaling": "auto" in text_lower and "scal" in text_lower
            }
        }
    
    def extract_financial_features(vendor_text: str, vendor_name: str) -> dict:
        """Extract financial features from vendor text"""
        text_lower = vendor_text.lower()
        
        return {
            "total_cost_ownership": {
                "tco_3year": extract_cost_amount(vendor_text),
                "cost_breakdown_provided": "breakdown" in text_lower,
                "transparent_pricing": "transparent" in text_lower
            },
            "pricing_model": {
                "pricing_model": determine_pricing_model(vendor_text),
                "volume_discounts": "discount" in text_lower,
                "flexible_pricing": "flexible" in text_lower
            },
            "payment_terms": {
                "payment_terms": extract_payment_terms(vendor_text),
                "milestone_payments": "milestone" in text_lower,
                "warranty_included": "warranty" in text_lower
            }
        }
    
    def extract_vendor_features(vendor_text: str, vendor_name: str) -> dict:
        """Extract vendor experience features"""
        text_lower = vendor_text.lower()
        
        return {
            "company_experience": {
                "years_in_business": extract_years_experience(vendor_text),
                "similar_projects": extract_project_count(vendor_text),
                "industry_expertise": "industry" in text_lower
            },
            "project_references": {
                "references": extract_client_references(vendor_text),
                "reference_quality": "enterprise" in text_lower or "fortune" in text_lower,
                "recent_projects": any(year in vendor_text for year in ["2023", "2024", "2025"])
            },
            "certifications": {
                "certifications": [kw.upper() for kw in ['certification', 'certified', 'iso', 'soc', 'pci'] if kw in text_lower],
                "relevant_certifications": len([kw for kw in ['iso', 'soc', 'pci'] if kw in text_lower]) > 1
            }
        }
    
    def extract_implementation_features(vendor_text: str, vendor_name: str) -> dict:
        """Extract implementation features"""
        text_lower = vendor_text.lower()
        
        return {
            "implementation_methodology": {
                "methodology": determine_methodology(vendor_text),
                "detailed_methodology": "detailed" in text_lower and "methodology" in text_lower,
                "risk_management": "risk" in text_lower and "management" in text_lower,
                "quality_assurance": "quality" in text_lower or "qa" in text_lower
            },
            "timeline": {
                "implementation_timeline": extract_timeline_months(vendor_text),
                "realistic_timeline": "realistic" in text_lower,
                "milestone_based": "milestone" in text_lower
            },
            "project_management": {
                "dedicated_pm": "dedicated" in text_lower and ("pm" in text_lower or "project manager" in text_lower),
                "project_tracking": "tracking" in text_lower,
                "regular_reporting": "reporting" in text_lower,
                "stakeholder_management": "stakeholder" in text_lower
            }
        }
    
    # Helper extraction functions
    def extract_cost_amount(text: str) -> str:
        import re
        cost_patterns = [r'\$[\d,]+', r'USD [\d,]+', r'[\d,]+ USD']
        for pattern in cost_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return "Cost information available"
    
    def determine_pricing_model(text: str) -> str:
        text_lower = text.lower()
        if "subscription" in text_lower:
            return "subscription"
        elif "license" in text_lower:
            return "licensing"
        elif "saas" in text_lower:
            return "saas"
        return "standard"
    
    def extract_payment_terms(text: str) -> str:
        text_lower = text.lower()
        if "net 30" in text_lower:
            return "net 30"
        elif "net 60" in text_lower:
            return "net 60"
        return "standard terms"
    
    def extract_years_experience(text: str) -> str:
        import re
        patterns = [r'(\d+) years?', r'established (\d{4})', r'founded (\d{4})']
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return str(matches[0])
        return "Experience mentioned"
    
    def extract_project_count(text: str) -> str:
        import re
        patterns = [r'(\d+) projects?', r'(\d+) implementations?']
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return str(matches[0])
        return "Multiple projects"
    
    def extract_client_references(text: str) -> list:
        references = []
        text_lower = text.lower()
        if "fortune 500" in text_lower:
            references.append("Fortune 500 clients")
        if "enterprise" in text_lower:
            references.append("Enterprise clients")
        if "government" in text_lower:
            references.append("Government clients")
        return references if references else ["References available"]
    
    def determine_methodology(text: str) -> str:
        text_lower = text.lower()
        if "agile" in text_lower:
            return "agile"
        elif "waterfall" in text_lower:
            return "waterfall"
        elif "devops" in text_lower:
            return "devops"
        return "standard"
    
    def extract_timeline_months(text: str) -> str:
        import re
        patterns = [r'(\d+) months?', r'(\d+) weeks?']
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if "week" in pattern:
                    return f"{int(int(matches[0])/4)} months"
                return f"{matches[0]} months"
        return "Timeline provided"
    
    def process_single_vendor(vendor_path: str, expected_vendor: str) -> dict:
        """Process a single vendor folder"""
        if not vendor_path or vendor_path.strip() == "":
            return {
                'vendor_name': expected_vendor,
                'vendor_text': f"No path provided for {expected_vendor}",
                'processed_files': [],
                'total_files': 0,
                'status': 'no_path_provided',
                'technical_data': {},
                'financial_data': {},
                'vendor_data': {},
                'implementation_data': {},
                'extraction_summary': {'features_extracted': False}
            }
        
        vendor_name, exact_match, vendor_key = identify_vendor_from_path(vendor_path)
        
        # Get vendor-specific file list
        if vendor_key in VENDOR_CONFIG:
            files_to_try = VENDOR_CONFIG[vendor_key]["expected_files"] + [
                "financial_proposal.pdf", "executive_summary.pdf", "pricing_document.pdf",
                "architecture_diagram.svg", "implementation_timeline.svg"
            ]
        else:
            files_to_try = ["technical_proposal.pdf", "commercial_proposal.pdf", "company_qualifications.pdf"]
        
        print(f"Processing {vendor_name} from: {vendor_path}")
        
        # Read all files
        all_content = ""
        processed_files = []
        
        for filename in files_to_try:
            file_uri = f"{vendor_path.rstrip('/')}/{filename}"
            content = None
            
            try:
                if filename.endswith('.pdf'):
                    content = read_pdf_from_uri(file_uri)
                elif filename.endswith('.svg'):
                    content = read_svg_from_uri(file_uri)
                
                if content:
                    all_content += f"\n\n=== {filename} ===\n{content}"
                    processed_files.append(filename)
                    print(f"✅ {vendor_name}: Processed {filename}")
            except Exception as e:
                print(f"❌ {vendor_name}: Failed {filename} - {str(e)}")
        
        # Extract features if we have content
        if all_content and len(all_content.strip()) > 100:
            print(f"🔍 {vendor_name}: Extracting features from {len(all_content)} characters")
            
            return {
                'vendor_name': vendor_name,
                'vendor_folder': vendor_path,
                'vendor_text': all_content,
                'processed_files': processed_files,
                'total_files': len(processed_files),
                'status': 'success',
                'technical_data': extract_technical_features(all_content, vendor_name),
                'financial_data': extract_financial_features(all_content, vendor_name),
                'vendor_data': extract_vendor_features(all_content, vendor_name),
                'implementation_data': extract_implementation_features(all_content, vendor_name),
                'path_validation': {
                    'exact_match': exact_match,
                    'expected_path': VENDOR_CONFIG.get(vendor_key, {}).get('expected_path', ''),
                    'actual_path': vendor_path
                },
                'extraction_summary': {
                    'document_length': len(all_content),
                    'files_processed': len(processed_files),
                    'extraction_complete': True,
                    'features_extracted': True
                }
            }
        else:
            print(f"⚠️ {vendor_name}: Insufficient content for feature extraction")
            return {
                'vendor_name': vendor_name,
                'vendor_folder': vendor_path,
                'vendor_text': all_content or f"No readable content found for {vendor_name}",
                'processed_files': processed_files,
                'total_files': len(processed_files),
                'status': 'insufficient_content',
                'technical_data': {},
                'financial_data': {},
                'vendor_data': {},
                'implementation_data': {},
                'extraction_summary': {'features_extracted': False}
            }
    
    # Main execution
    try:
        print("Multi_Vendor_Reader: Processing both Cyberguard and SecureNet...")
        
        # Process both vendors
        cyberguard_data = process_single_vendor(vendor_proposal_1, "Cyberguard")
        securenet_data = process_single_vendor(vendor_proposal_2, "SecureNet")
        
        # Create combined output
        result = {
            "status": "success",
            "vendors_processed": 2,
            "vendors": [cyberguard_data, securenet_data],
            "processing_summary": {
                "cyberguard_status": cyberguard_data['status'],
                "securenet_status": securenet_data['status'],
                "both_vendors_ready": all(v['extraction_summary']['features_extracted'] for v in [cyberguard_data, securenet_data]),
                "total_files_processed": cyberguard_data['total_files'] + securenet_data['total_files']
            },
            "extraction_metadata": {
                "extraction_method": "multi_vendor_reader_with_features",
                "features_extracted": ["technical_data", "financial_data", "vendor_data", "implementation_data"],
                "ready_for_scoring_engine": True,
                "timestamp": "2025-07-14T12:00:00Z"
            }
        }
        
        print(f"✅ Multi_Vendor_Reader completed:")
        print(f"   - Cyberguard: {cyberguard_data['status']} ({cyberguard_data['total_files']} files)")
        print(f"   - SecureNet: {securenet_data['status']} ({securenet_data['total_files']} files)")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Multi-vendor processing failed: {str(e)}",
            "vendors": [],
            "ready_for_scoring_engine": False
        }
        return json.dumps(error_result, indent=2)