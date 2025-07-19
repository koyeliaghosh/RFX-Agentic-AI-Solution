from promptflow import tool
import requests
import PyPDF2
import io

@tool
def File_Reader(input1: str) -> dict:
    """
    Read PDF files from RFP folder containing multiple documents
    """
    
    def read_pdf_from_uri(blob_uri: str) -> str:
        try:
            if not blob_uri:
                return "No URI provided"
            
            print(f"Reading from URI: {blob_uri}")
            
            # Download the PDF file
            response = requests.get(blob_uri, timeout=60)
            
            if response.status_code == 200:
                # Read PDF content
                pdf_file = io.BytesIO(response.content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Extract text from all pages
                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                
                return text_content.strip()
            else:
                return None
        except Exception as e:
            return None
    
    # Common RFP document names to try
    rfp_files = [
        "Enterprise%20Network%20RFP%20document.pdf",
        "rfp_document.pdf",
        "network_security_rfp.pdf",
        "enterprise_rfp.pdf"
    ]
    
    all_rfp_content = ""
    processed_files = []
    
    # Try to read RFP files from the folder
    for filename in rfp_files:
        file_uri = f"{input1.rstrip('/')}/{filename}"
        content = read_pdf_from_uri(file_uri)
        
        if content:
            all_rfp_content += f"\n\n=== {filename} ===\n{content}"
            processed_files.append(filename)
    
    return {
        "rfp_text": all_rfp_content if all_rfp_content else "No RFP documents found",
        "processed_files": processed_files,
        "rfp_folder": input1,
        "status": f"Processed {len(processed_files)} RFP files successfully"
    }