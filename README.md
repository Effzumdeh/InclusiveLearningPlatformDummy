# Inklusive Lernplattform – Prototyp

Dies ist ein Prototyp einer inklusiven Online-Lernplattform. Er besteht aus:
- **Backend:** Implementiert mit FastAPI (Python)
- **Frontend:** Implementiert mit Vue.js

## Voraussetzungen

- Python 3.8 oder höher
- Node.js (empfohlen Version 14 oder höher)
- npm (Node Package Manager)

## Backend starten

1. Wechsle in das `backend`-Verzeichnis:
   ```bash
   cd backend
2. Erstelle und aktiviere ein virtuelles Environment (optional):
    python -m venv venv
    source venv/bin/activate      # Linux/Mac
    venv\Scripts\activate         # Windows
3. Installiere die benötigten Pakete:
    pip install -r requirements.txt
4. Starte den FastAPI-Server:
    uvicorn main:app --reload
Der Server läuft nun unter http://127.0.0.1:8000.

## Frontend starten
1. Wechsle in das frontend-Verzeichnis:
    cd frontend
2. Installiere die npm-Abhängigkeiten:
    npm install
3. Starte den Entwicklungsserver:
    npm run serve
Die Anwendung ist dann unter http://localhost:8080 erreichbar.
