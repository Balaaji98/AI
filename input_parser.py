from docx import Document

def extract_text_from_docx(file_path):
    """
    Extracts text from a Word document (.docx).
    
    Args:
        file_path (str): Path to the Word document.
    
    Returns:
        str: Extracted text from the document.
    """
    try:
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return text
    except Exception as e:
        print(f"Error reading Word document: {e}")
        return ""

# Test the function with the sample requirement document
if __name__ == "__main__":
    file_path = '/Users/balaajiganesh/Library/Mobile Documents/com~apple~CloudDocs/WMS-AI-DESIGN-AGENT/sample_requirement.docx'
    extracted_text = extract_text_from_docx(file_path)
    print("Extracted Text:\n")
    print(extracted_text)