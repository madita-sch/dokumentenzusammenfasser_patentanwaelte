# Packages und libraries laden
import dash
import threading
import os
import base64
import dash_bootstrap_components as dbc
import logging
from dash import Dash, html, dcc, Input, Output, State
from pdf_utils import extract_text_from_pdf
from summarizer import DocumentSummarizer

# Working Directory festlegen
os.chdir(r"C:\Users\Lenovo\Desktop\Mathe\Projekt Machine Learning\dokumentenzusammenfasser")

# Dash App
app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
summarizer = DocumentSummarizer()

# Globale Variablen für Thread und Fortschritt definieren
progress_messages = []
summary_result = None
summary_thread = None
total_chunks = 0
done_chunks = 0

# Passwort fuer Login
PASSWORD = "TESTPW1234"

# Erstellung des Layouts
app.layout = html.Div([
    # Login-Bereich
    html.Div(id="login-div", children=[
        html.H2("Bitte einloggen"),
        dcc.Input(id="pw-input", type="password", placeholder="Passwort eingeben"),
        html.Button("Login", id="login-btn"),
        html.Div(id="login-msg", style={"color": "red", "marginTop": "10px"})
    ]),
    
    # Tatsaechliche App, die zunaechst versteckt ist
    html.Div(id="main-app", style={"display": "none"}, children=[
        html.H2("PDF-Dokumentenzusammenfasser für Patentanwälte",
                style={"backgroundColor":"#ADD8E6"}),

        dcc.Upload(
            id="upload-pdf",
            children=html.Button(["PDF hier hochladen"]),
            style={
                "width": "100%",
                "cursor": "pointer"
            },
        ),
        html.Div(id="upload-status", style={"marginTop": "2px", "color": "green"}),

        html.Button("Zusammenfassung generieren", id="summarize-btn",
                    style={
                        "backgroundColor":"lightblue"}),

        html.H2("Die Erstellung der Zusammenfassung dauert einige Sekunden.",
                style={"color":"#808080","fontStyle":"italic",
                       "fontSize":"12px"}),

        html.H4("Fortschritt"),

        dcc.Interval(id="progress-interval", interval=500, n_intervals=0),

        dbc.Progress(
            id="progress-bar",
            value=0,
            max=100,
            striped=True,
            animated=True,
            label="0 %",
            style={"height": "30px"}
        ),

        dcc.Textarea(
            id="progress-output",
            style={"width": "100%", "height": "80px"},
            readOnly=True
        ),

        html.H4("Zusammenfassung"),
        dcc.Textarea(id="summary-output", style={"width": "100%", "height": "250px"}),

        html.Br(),

        html.Button("Zusammenfassung herunterladen", id="download-btn",
                    style={
                        "backgroundColor":"#4CAF50"}),
        dcc.Download(id="download-summary"),
    ])
])


### Callbacks erstellen
# Callback für Login
@app.callback(
    Output("login-msg", "children"),
    Output("main-app", "style"),
    Output("login-div", "style"), #Login Bereich ausblenden
    Input("login-btn", "n_clicks"),
    State("pw-input", "value"),
    prevent_initial_call=True
)
def check_password(n_clicks, pw):
    if pw == PASSWORD:
        return "✅ Zugriff gewährt", {"display": "block"}, {"display": "none"}
    return "❌ Falsches Passwort", {"display": "none"}, {"display": "none"}

# Callbacks fuer Website
# Callback um Uploadstatus zu zeigen
@app.callback(
    Output("upload-status", "children"),
    Input("upload-pdf", "contents"),
    State("upload-pdf", "filename"),
)
def show_upload_status(contents, filename):

    if contents is None:
        return html.Div("Bitte lade eine PDF-Datei hoch.", style=
                        {"color":"gray","fontStyle":"italic",
                         "fontSize":"12px"})
    
    if not filename.lower().endswith(".pdf"):
        return "❌ Falsches Format - Bitte nur PDF-Dateien hochladen."
    return f"✅ Datei erfolgreich hochgeladen: {filename}"

# Callback um summary auszufuehren
@app.callback(
    Input("summarize-btn", "n_clicks"),
    State("upload-pdf", "contents"),
    prevent_initial_call=True
)
def start_summary(n_clicks, contents):
    global progress_messages, summary_result, summary_thread, total_chunks, done_chunks
    total_chunks = 0
    done_chunks = 0
    progress_messages = []
    summary_result = None

    # Pruefe ob PDF hochgeladen wurde
    if not contents:
        progress_messages.append("❌ Keine PDF-Datei hochgeladen")
        return

    # Extrahiere Text aus der PDF-Datei
    text = extract_text_from_pdf(contents)

    # Angabe des Fortschritts
    def progress_callback(done, total):
        global done_chunks, total_chunks
        total_chunks = total
        done_chunks = done
        progress_messages.append(f"Chunk {done}/{total} verarbeitet...")

    # Funktion definieren, die PDF-Zusammenfassung erstellt und Fortschritt meldet
    def summarize_thread_func():
        global summary_result
        summary_result = summarizer.summarize(text, progress_callback=progress_callback) # Aufruf Zusammenfassung
        progress_messages.append("✅ Zusammenfassung abgeschlossen") # Angabe Fortschrittsmeldung

    # Thread starten, damit Weboberflaeche reaktionsfaehig bleibt
    summary_thread = threading.Thread(target=summarize_thread_func)
    summary_thread.start()

# Callback fuer Progress Bar
@app.callback(
    Output("progress-bar", "value"),
    Output("progress-bar", "label"),
    Input("progress-interval", "n_intervals"),
)
def update_bar(n):
    global total_chunks, done_chunks
    if total_chunks ==0:
        return 0, "0 %"
    done = min(done_chunks, total_chunks)  # nicht größer als total
    percent = int((done / total_chunks) * 100)
    return percent, f"{percent} %"

# Callback fuer Text ueber Progress
@app.callback(
    Output("progress-output", "value"),
    Output("summary-output", "value"),
    Input("progress-interval", "n_intervals"),
)
def update_progress(n):
    global progress_messages, summary_result

    progress_text = "\n".join(progress_messages)

    if summary_result is not None:
        return progress_text, summary_result
    return progress_text, dash.no_update

# Callback fuer den Download der Zusammenfassung
@app.callback(
    Output("download-summary", "data"),
    Input("download-btn", "n_clicks"),
    State("summary-output", "value"),
    prevent_initial_call=True
)
def download_summary(n_clicks, summary_text):
    return dict(
        content=summary_text,
        filename="zusammenfassung.txt"
    )

# App starten
# Unterdrücke alle Flask-Request-Logs, um nur Error im Terminal zu sehen
logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

# Unterdrücke die internen Dash-Logs, um nur Error im Terminal zu sehen
logging.getLogger('dash').setLevel(logging.CRITICAL)

if __name__ == "__main__":
    app.run(debug=False)
