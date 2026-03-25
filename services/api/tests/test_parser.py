import pytest
from app.services.parser import DocumentParser

def test_parse_text():
    content = b"Hello World"
    result = DocumentParser.parse_text(content)
    assert result == "Hello World"

def test_parse_text_utf8():
    content = "Hello 🌍".encode("utf-8")
    result = DocumentParser.parse_text(content)
    assert result == "Hello 🌍"

def test_parse_unsupported():
    with pytest.raises(ValueError):
        DocumentParser.parse("test.exe", b"binary")

def test_parse_routing_txt():
    content = b"Plain text"
    result = DocumentParser.parse("test.txt", content)
    assert result == "Plain text"

def test_parse_routing_md():
    content = b"# Markdown"
    result = DocumentParser.parse("test.md", content)
    assert result == "# Markdown"

# For PDF and DOCX, we mock the libraries to avoid needing real files in the repo
def test_parse_pdf_mock(mocker):
    mock_fitz = mocker.patch("fitz.open")
    mock_doc = mock_fitz.return_value.__enter__.return_value
    mock_page = mocker.MagicMock()
    mock_page.get_text.return_value = "PDF Content"
    mock_doc.__iter__.return_value = [mock_page]
    
    result = DocumentParser.parse_pdf(b"fake pdf")
    assert "PDF Content" in result
    mock_fitz.assert_called_once()

def test_parse_docx_mock(mocker):
    mock_docx = mocker.patch("app.services.parser.Document")
    mock_doc = mock_docx.return_value
    mock_para = mocker.MagicMock()
    mock_para.text = "DOCX Content"
    mock_doc.paragraphs = [mock_para]
    
    result = DocumentParser.parse_docx(b"fake docx")
    assert result == "DOCX Content"
    mock_docx.assert_called_once()
