import random
from typing import Dict, Tuple


def score_for_image(name: str) -> Tuple[float, str]:
    """Demo heuristic: deterministic pseudo-random score based on filename."""
    seed = hash(name) % 10_000
    rng = random.Random(seed)
    score = rng.uniform(0, 1)

    # Lightweight intent guess based on filename hints
    lower = name.lower()
    if "knife" in lower or "weapon" in lower:
        intent = "threatening_object"
        score = max(score, 0.8)
    elif "crowd" in lower or "group" in lower:
        intent = "crowd_activity"
    elif "fire" in lower or "smoke" in lower:
        intent = "hazard_fire"
        score = max(score, 0.85)
    else:
        intent = "unknown_intent"

    return round(score, 3), intent


def level_for_score(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def analyze_frame(filename: str) -> Dict:
    score, intent = score_for_image(filename)
    level = level_for_score(score)
    return {"filename": filename, "score": score, "intent": intent, "level": level}

