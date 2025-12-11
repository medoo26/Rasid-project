# Risk Alert Demo

Demo of intent-aware risk detection with owner verification and secure alert dispatch. The camera feed is simulated from local images.

## Prerequisites
- Python 3.10+
- Node.js 18+

## Backend (FastAPI)
1) Install deps:
```
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
```
2) Configure environment:
- Copy `env.example` to `.env` and adjust `IMAGE_FOLDER`, `SIGNING_SECRET`, `AUTHORITY_API_URL`, `PORT`.
- Place sample images in `sample_images/` (or update the path).
3) Run:
```
uvicorn main:app --reload --port 8000
```
Static images are served at `/static/<filename>`.

## Frontend (React + Vite)
1) Install deps:
```
cd frontend
npm install
```
2) Configure:
- Copy `env.example` to `.env` if you need a different API base.
3) Run dev server:
```
npm run dev
```
Open the URL shown (default http://localhost:5173).

## Flow
- Backend cycles through images on each `POST /analyze`, generating a risk score and intent.
- Medium risk opens a 2-minute verification window for the owner (confirm vs false alarm).
- High risk or verification timeout triggers a digitally signed alert dispatched to the configured authority API (mocked client).
- Frontend displays the feed, risk level, verification countdown, and alert payload status.

