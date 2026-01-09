# dokumentenzusammenfasser_patentanwaelte
Dieses GitHub Repository enthält alle notwendigen Skripts für den Dokumentenzusammenfasser für Patentanwälte im Rahmen des Projekts Machine Learning Systems Design (DLMDSPMLSD01_D).

### How to use 
1. Installiere dependencies: pip install -r requirements.txt
2. Run the pdf_utils script: python pdf_utils.py
3. Run the summarizer script: python summarizer.py
4. Run the app script: python app.py

### How to test/evaluate 
1. Run the pytest script: pytest -v
2. Run the modellbewertung script fuer ROUGE score: python modellbewertung.py

## Dataset Getestet mit dem CNN/DailyMail Datensatz und basiert auf DistilBART (sshleifer/distilbart-cnn-12-6).
