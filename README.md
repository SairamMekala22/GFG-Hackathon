# AI Dashboard Generator

Production-grade prototype for natural-language business dashboards built with React, Flask, SQLite, Pandas, Gemini, Recharts, and Socket.IO.

## Structure

- `frontend/`: Vite + React + Tailwind UI with prompt input, voice capture, CSV upload, draggable dashboard widgets, PDF export, and live session sync.
- `backend/`: Flask API with Gemini-powered SQL generation, self-healing SQL retries, chart selection, insight generation, CSV-to-SQLite ingestion, rate limiting, and Socket.IO collaboration.

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python app.py
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The backend defaults to port `5050` locally. Set `VITE_API_URL` and `VITE_SOCKET_URL` if the backend is hosted elsewhere.
