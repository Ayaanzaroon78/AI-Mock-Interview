import io
import pytest
from backend.resume_service import extract_resume


class Upload:
    def __init__(self, name, data): self.filename, self.data = name, data
    def read(self, size=-1): return self.data[:size]


def test_rejects_unsupported_type():
    with pytest.raises(ValueError, match="PDF or DOCX"):
        extract_resume(Upload("resume.txt", b"hello"))


def test_rejects_empty_and_oversized():
    with pytest.raises(ValueError, match="empty"):
        extract_resume(Upload("resume.pdf", b""))
    with pytest.raises(ValueError, match="4 MB"):
        extract_resume(Upload("resume.pdf", b"%PDF-" + b"x" * 100), max_bytes=50)


def test_rejects_malformed_signature():
    with pytest.raises(ValueError, match="valid PDF"):
        extract_resume(Upload("resume.pdf", b"not a pdf"))


def test_extracts_docx_and_rejects_insufficient_text():
    from docx import Document
    out=io.BytesIO();doc=Document();doc.add_paragraph("Python Flask SQL REST API and application development experience." * 2);doc.save(out)
    text=extract_resume(Upload("resume.docx",out.getvalue()))
    assert "Python Flask SQL" in text
    from pypdf import PdfWriter
    pdf=io.BytesIO();writer=PdfWriter();writer.add_blank_page(width=72,height=72);writer.write(pdf)
    with pytest.raises(ValueError,match="Not enough readable text"):
        extract_resume(Upload("resume.pdf",pdf.getvalue()),minimum=30)
