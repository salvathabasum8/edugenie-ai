import io
import re

class PDFService:
    @staticmethod
    def extract_text_from_bytes(file_bytes, filename="document.pdf"):
        """Extracts text from PDF or text bytes with graceful fallbacks."""
        filename_lower = filename.lower()
        
        # If text file, decode directly
        if filename_lower.endswith((".txt", ".md", ".json", ".csv")):
            try:
                return file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return file_bytes.decode("latin-1", errors="ignore")

        # Try pypdf / PyPDF2 / pdfplumber if installed
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            if text.strip():
                return text.strip()
        except ImportError:
            pass

        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            if text.strip():
                return text.strip()
        except ImportError:
            pass

        # Fallback simple stream text extractor for raw PDF buffers
        try:
            raw = file_bytes.decode("latin-1", errors="ignore")
            # Extract text streams in PDF: (BT ... ET)
            matches = re.findall(r"\((.*?)\)", raw)
            extracted = " ".join([m for m in matches if len(m) > 2 and not m.startswith("/")])
            if len(extracted) > 100:
                return extracted[:10000]
        except Exception:
            pass

        return "Could not parse PDF text. Please paste the text content directly."

    @staticmethod
    def summarize_document(text, max_length=3000):
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned[:max_length]
