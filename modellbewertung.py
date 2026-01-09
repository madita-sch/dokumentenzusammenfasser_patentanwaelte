### Modellbewertung mithilfe von Rouge 
### ROUGE (Recall-Oriented Understudy for Gisting Evaluation) als Standard
### fuer automatische Textzusammenfassung

import time
import os
from rouge_score import rouge_scorer
from datasets import load_dataset
from summarizer import DocumentSummarizer

# WD festlegen
os.chdir(r"C:\Users\Lenovo\Desktop\Mathe\Projekt Machine Learning\dokumentenzusammenfasser")

# Initialisierung summarizer modell 
summarizer = DocumentSummarizer(max_words=120)

# Testdatenset CNN/Dailymail laden
dataset = load_dataset("cnn_dailymail", "3.0.0", split="test[:20]")


# Rouge initialisieren
scorer = rouge_scorer.RougeScorer(
    ["rouge1", "rouge2", "rougeL"],
    use_stemmer=True
)

rouge1, rouge2, rougeL = [], [], []

# Bewertung / Berechnung von ROUGE
start_time = time.time()

for idx, sample in enumerate(dataset, 1):
    article = sample["article"]
    reference = sample["highlights"]

    # Dynamische Anpassung der max_words (10–20 Wörter)
    input_len = len(article.split())
    max_words_eval = max(10, min(50, int(input_len * 0.4)))
    
    # Wenn nötig, neuen Summarizer mit angepasster Länge erstellen
    if summarizer.max_words != max_words_eval:
        summarizer = DocumentSummarizer(max_words=max_words_eval)

    # max_length dynamisch an Textlänge anpassen
    max_length = max(10, min(20, input_len))
    min_length = max(10, int(max_length * 0.3))

    # Zusammenfassung erzeugen
    summary = summarizer.summarize(article,max_length=max_length, min_length=min_length)
    
    # ROUGE-Berechnung
    scores = scorer.score(reference, summary)

    # Hinzufuegen der Werte
    rouge1.append(scores["rouge1"].fmeasure)
    rouge2.append(scores["rouge2"].fmeasure)
    rougeL.append(scores["rougeL"].fmeasure)

end_time = time.time()

print("ROUGE-1 F1:", sum(rouge1) / len(rouge1))
print("ROUGE-2 F1:", sum(rouge2) / len(rouge2))
print("ROUGE-L F1:", sum(rougeL) / len(rougeL))
print(f"Ø Laufzeit pro Dokument: {(end_time - start_time)/len(dataset):.2f} Sekunden")