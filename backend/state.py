from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


@dataclass
class VerificationWindow:
    started_at: datetime
    expires_at: datetime
    frame: str
    status: str = "pending"  # pending|confirmed|dismissed|expired


@dataclass
class RiskState:
    last_frame: Optional[str] = None
    last_score: float = 0.0
    last_level: str = "low"
    last_intent: str = "unknown_intent"
    verification: Optional[VerificationWindow] = None
    last_alert_payload: Optional[dict] = None
    history: list = field(default_factory=list)


class StateManager:
    def __init__(self) -> None:
        self.state = RiskState()

    def record_analysis(self, analysis: dict) -> None:
        self.state.last_frame = analysis["filename"]
        self.state.last_score = analysis["score"]
        self.state.last_level = analysis["level"]
        self.state.last_intent = analysis["intent"]
        self.state.history.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "frame": analysis["filename"],
                "score": analysis["score"],
                "level": analysis["level"],
                "intent": analysis["intent"],
            }
        )

    def ensure_verification_window(self, frame: str, ttl_seconds: int = 120) -> VerificationWindow:
        now = datetime.now(timezone.utc)
        vw = VerificationWindow(started_at=now, expires_at=now + timedelta(seconds=ttl_seconds), frame=frame)
        self.state.verification = vw
        return vw

    def clear_verification(self) -> None:
        self.state.verification = None

    def maybe_expire(self) -> bool:
        vw = self.state.verification
        if not vw:
            return False
        if datetime.now(timezone.utc) >= vw.expires_at and vw.status == "pending":
            vw.status = "expired"
            return True
        return False

    def serialize(self) -> dict:
        vw = self.state.verification
        return {
            "frame": self.state.last_frame,
            "score": self.state.last_score,
            "level": self.state.last_level,
            "intent": self.state.last_intent,
            "verification": None
            if not vw
            else {
                "started_at": vw.started_at.isoformat(),
                "expires_at": vw.expires_at.isoformat(),
                "frame": vw.frame,
                "status": vw.status,
            },
            "last_alert_payload": self.state.last_alert_payload,
            "history": self.state.history[-20:],
        }

