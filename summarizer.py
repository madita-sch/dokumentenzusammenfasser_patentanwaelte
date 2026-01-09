from transformers import pipeline
import re
import torch

# Erstelle eine Klasse zum Zusammenfassen von Textdokumenten mithilfe
# des vortrainierten Transformers-Modells DistilBART
class DocumentSummarizer:

    # Initialisieren des Summarizers, definiert Transformer Modell und 
    # max. Anzahl an Woertern pro Chunk, um lange Texte aufzuteilen
    def __init__(self, model_name="sshleifer/distilbart-cnn-12-6", max_words=500):
        self.model_name = model_name
        self.max_words = max_words
        self.summarizer = None

    # Laden des Modells, falls es noch nicht geladen wurde, um zu vermeiden,
    # dass das Modell mehrfach geladen wird
    def load_model(self):
        if self.summarizer is None:
            device = 0 if torch.cuda.is_available() else -1
            self.summarizer = pipeline("summarization", model=self.model_name, device=device)

    # Aufteilen des Texts in kleinere Chunks, um Effizienz des Modells zu steigern
    def chunk_text(self, text):
        words = text.split()
        for i in range(0, len(words), self.max_words):
            yield " ".join(words[i:i+self.max_words])

    # Bereinigung des Texts, entfernt unnoetige Leerzeichen & Formatierungsfehler
    def clean_text(self, text: str) -> str:
        # Leerzeichen vor Satzzeichen entfernen
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)
        # Mehrfache Leerzeichen reduzieren
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    # Zusammenfassung des Texts
    def summarize(self, text, max_length=400, min_length=50, progress_callback=None):
        
        # Modell laden, falls noch nicht geschehen
        self.load_model()

        # Instruction Prefixing an Modell
        prompt_prefix = (
            "Erstelle eine sachliche, präzise Zusammenfassung des folgenden "
            "technischen Dokuments. Behalte alle rechtlich relevanten Informationen:\n\n"
        )

        text = prompt_prefix + text

        # Wenn kurzer Text, bereinige und gebe zurueck
        words = text.split()
        if len(words) < min_length:
            return self.clean_text(text)

        # Text in chunks aufteilen
        chunks = list(self.chunk_text(text))
        summaries = []
        total = len(chunks)

        # Jeden Chunk zusammenfassen
        for i, chunk in enumerate(chunks, start=1):
            #Fortschritt melden
            if progress_callback:
                progress_callback(i, total)

            # Zusammenfassung des Chunks erzeugen
            result = self.summarizer(
                chunk,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )

            # Zusammenfassung speicher
            summaries.append(result[0]["summary_text"])

        # Alle Zusammenfassungen der Chunks zusammenfuegen
        full_summary = " ".join(summaries)

        # Endgueltige Bereinigung des Texts
        return self.clean_text(full_summary)
