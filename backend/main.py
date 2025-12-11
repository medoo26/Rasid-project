import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .authority_client import send_alert
from .config import settings
from .image_feed import ImageCursor, list_images
from .risk_engine import analyze_frame, level_for_score
from .state import StateManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Risk Alert Demo", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cursor = ImageCursor()
state_manager = StateManager()

app.mount("/static", StaticFiles(directory=settings.image_folder), name="static")


class AnalyzeResponse(BaseModel):
    filename: Optional[str]
    score: float
    level: str
    intent: str
    verification: Optional[dict]
    alert_dispatched: bool


class VerifyRequest(BaseModel):
    decision: str  # "confirm" | "false_alarm"


def maybe_send_alert(reason: str) -> Optional[dict]:
    payload = {
        "frame": state_manager.state.last_frame,
        "score": state_manager.state.last_score,
        "level": state_manager.state.last_level,
        "intent": state_manager.state.last_intent,
        "reason": reason,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    result = send_alert(payload)
    state_manager.state.last_alert_payload = {**payload, "dispatch_result": result}
    return result


def handle_verification_logic() -> bool:
    """Returns True if an alert was dispatched due to expiry."""
    expired = state_manager.maybe_expire()
    if expired and state_manager.state.verification:
        maybe_send_alert(reason="verification_timeout")
        return True
    return False


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/frames")
def frames() -> dict:
    return {"frames": list_images()}


@app.get("/state")
def get_state() -> dict:
    handle_verification_logic()
    return state_manager.serialize()


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_next() -> AnalyzeResponse:
    filename = cursor.next()
    if not filename:
        raise HTTPException(status_code=400, detail="No images available in image folder")

    analysis = analyze_frame(filename)
    state_manager.record_analysis(analysis)

    alert_dispatched = False

    if analysis["level"] == "high":
        maybe_send_alert(reason="high_risk")
        alert_dispatched = True
        state_manager.clear_verification()
    elif analysis["level"] == "medium":
        state_manager.ensure_verification_window(frame=filename)
    else:
        state_manager.clear_verification()

    alert_dispatched = alert_dispatched or handle_verification_logic()

    return AnalyzeResponse(
        filename=filename,
        score=analysis["score"],
        level=analysis["level"],
        intent=analysis["intent"],
        verification=state_manager.serialize()["verification"],
        alert_dispatched=alert_dispatched,
    )


@app.post("/verify")
def verify(req: VerifyRequest) -> dict:
    vw = state_manager.state.verification
    if not vw:
        raise HTTPException(status_code=400, detail="No active verification window")

    handle_verification_logic()
    vw = state_manager.state.verification
    if not vw or vw.status != "pending":
        raise HTTPException(status_code=400, detail="Verification window closed")

    if req.decision not in {"confirm", "false_alarm"}:
        raise HTTPException(status_code=400, detail="Invalid decision")

    alert_dispatched = False
    if req.decision == "confirm":
        vw.status = "confirmed"
        maybe_send_alert(reason="owner_confirmed")
        alert_dispatched = True
    else:
        vw.status = "dismissed"

    return {
        "verification": state_manager.serialize()["verification"],
        "alert_dispatched": alert_dispatched,
    }


@app.post("/alert")
def trigger_alert() -> dict:
    """Manual trigger for testing."""
    res = maybe_send_alert(reason="manual_trigger")
    return {"dispatched": res is not None, "result": res}


@app.get("/current-frame")
def current_frame() -> dict:
    return {"current": cursor.current()}


def _demo_run() -> None:
    import uvicorn  # type: ignore

    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)


if __name__ == "__main__":
    _demo_run()

