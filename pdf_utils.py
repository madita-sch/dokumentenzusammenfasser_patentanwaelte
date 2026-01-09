# Packages und Libraries laden
from pypdf import PdfReader
import io
import base64

# Funktion definieren, die Text aus einer hochgeladenen PDF-Datei extrahiert, 
# die als als Base64-codierter string vorliegt.
def extract_text_from_pdf(contents):
    # Trennung von Header und Base64-Daten
    content_type, content_string = contents.split(",")
    # Base64-Decodierung, um in Text umzuwandeln
    pdf_bytes = base64.b64decode(content_string)
    # Bytes in einen Dateistream umwandeln, den PdfReader lesen kann
    pdf_file = io.BytesIO(pdf_bytes)

    #PDF-Datei mit PyPDF oeffnen
    reader = PdfReader(pdf_file)
    text = "" #sammelt Text

    # Iteration durch alle Seiten der PDF-Datei, hinzufuegen des Texts
    for page in reader.pages:
        page_text = page.extract_text() 
        if page_text:
            text += page_text + "\n"

    # Ueberfluessige Leerzeichen am Anfang & Ende entfernen
    return text.strip() 