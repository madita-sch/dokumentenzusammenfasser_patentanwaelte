### Notiz: Lassen Sie dieses Script in cmd Terminal laufen unter "pytest -v"

# Packages und libraries laden
from datasets import load_dataset
from rouge_score import rouge_scorer
import json
import base64
import io
import pytest
from reportlab.pdfgen import canvas
import os

# Korrektes Working Directory
print(os.getcwd())
os.chdir("C:/Users/Lenovo/Desktop/Mathe/Projekt Machine Learning/dokumentenzusammenfasser")


# Unit Tests mit pytest, um Logik zu testen

# Textextraktion testen
# Textextraktion: Text wird extrahiert
# Text extractions funktion laden
from pdf_utils import extract_text_from_pdf

# Hilfsfunktion, um eine kleine PDF im Speicher zu erzeugen
def create_base64_pdf(text: str) -> str:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:application/pdf;base64,{encoded}"
def test_extract_text_from_pdf_success():
    contents = create_base64_pdf("Hello PDF World")

    text = extract_text_from_pdf(contents)

    assert isinstance(text, str)
    assert "Hello PDF World" in text

# Textextraktion: Leerzeichen entfernt
def test_extract_leerzeichen_entfernt():
    contents = create_base64_pdf("  Test Text  ")

    text = extract_text_from_pdf(contents)

    assert text == text.strip()

# Textextraktion: Leerzeichen entfernt
def test_extract_text_empty_pdf():
    buffer = io.BytesIO()
    canvas.Canvas(buffer).save()

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    contents = f"data:application/pdf;base64,{encoded}"

    text = extract_text_from_pdf(contents)

    assert text == ""

# Textextraktion: Leere PDF = leerer String 
def test_extract_text_empty_pdf():
    buffer = io.BytesIO()
    canvas.Canvas(buffer).save()

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    contents = f"data:application/pdf;base64,{encoded}"

    text = extract_text_from_pdf(contents)

    assert text == ""

# Textextraktion: Fehler bei ungueltigem base64
def test_extract_text_invalid_base64():
    contents = "data:application/pdf;base64,INVALID_BASE64"

    with pytest.raises(Exception):
        extract_text_from_pdf(contents)

# Zusammenfassungs-funktion testen 
# Funktion aus summarizer.py laden
from summarizer import DocumentSummarizer

@pytest.fixture
def summarizer():
    return DocumentSummarizer(max_words=40)

# Test Artikel
TEST_ARTICLE = """
Artificial intelligence is transforming many industries.
Companies are increasingly adopting machine learning models
to automate processes, analyze data, and improve decision-making.
However, challenges such as data privacy, bias, and transparency
remain significant concerns for researchers and policymakers.
"""
# Summarize-Funktion auf Test Artikel testen
def test_summarizer_with_text(summarizer):
    summary = summarizer.summarize(
        TEST_ARTICLE,
        max_length=50,
        min_length=30
    )

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert summary != TEST_ARTICLE

# Zusammenfassung Test: Viele Leerzeichen werden entfernt
def test_clean_text_handles_multiple_spaces(summarizer):
    text = "Dies  ist  ein  Test      ,  mit vielen    Leerzeichen  !"
    cleaned = summarizer.clean_text(text)
    assert "  " not in cleaned
    assert "  ," not in cleaned
    assert cleaned.endswith("!")


@pytest.fixture
def summarizer():
    # Für diesen Test max_words=5, nur zum Testen von chunk_text
    return DocumentSummarizer(max_words=5)

# Zusammenfassung Test: Chunks werden korrekt erstellt
def test_chunk_text_splits_correctly(summarizer):
    text = "eins zwei drei vier fünf sechs sieben acht neun zehn"
    chunks = list(summarizer.chunk_text(text))
    assert len(chunks) == 2  
    assert all(isinstance(c, str) for c in chunks)
    assert "eins zwei drei vier fünf" in chunks[0]
    assert "sechs sieben acht neun zehn" in chunks[1]


