from docx import Document

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():  # skip empty lines
                full_text.append(para.text.strip())
        return "\n".join(full_text)
    except Exception as e:
        return f"[ERROR] Failed to read docx: {e}"
