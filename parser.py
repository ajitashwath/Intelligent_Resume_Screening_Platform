# parser.py
import fitz  # this is PyMuPDF

def extract_text_from_pdf(file_path):
    """Takes a path to a PDF resume, returns its full text as a string."""
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

# --- Test it standalone ---
if __name__ == "__main__":
    sample_text = extract_text_from_pdf("resumes/sample1.pdf")
    print(sample_text)