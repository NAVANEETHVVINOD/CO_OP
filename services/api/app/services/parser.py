import io
import fitz  # PyMuPDF
from docx import Document

class DocumentParser:
    """
    Parses various document formats into raw text.
    Supported: PDF, DOCX, TXT, MD.
    """
    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        text = ""
        # fitz.open requires a stream or filename, we can pass stream
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text

    @staticmethod
    def parse_text(file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8", errors="replace")

    @classmethod
    def parse(cls, filename: str, file_bytes: bytes) -> str:
        ext = filename.split(".")[-1].lower()
        if ext == "pdf":
            return cls.parse_pdf(file_bytes)
        elif ext in ["doc", "docx"]:
            return cls.parse_docx(file_bytes)
        elif ext in ["txt", "md", "csv", "json"]:
            return cls.parse_text(file_bytes)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

parser = DocumentParser()
