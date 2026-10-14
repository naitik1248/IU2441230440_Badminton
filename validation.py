"""
validation.py
Input validation helpers for the application.
"""

from datetime import datetime
from typing import Dict, Tuple


def validate_match(data: Dict) -> Tuple[bool, str]:
    """Validate a match record before saving it."""
    required = ["date", "opponent", "event", "result", "points_for", "points_against"]
    for field in required:
        if not str(data.get(field, "")).strip():
            return False, f"{field.replace('_', ' ').title()} is required."

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return False, "Date must use YYYY-MM-DD format."

    if data["result"] not in {"Win", "Loss"}:
        return False, "Result must be Win or Loss."

    try:
        pf = int(data["points_for"])
        pa = int(data["points_against"])
    except (TypeError, ValueError):
        return False, "Points for and points against must be whole numbers."

    if pf < 0 or pa < 0:
        return False, "Points cannot be negative."

    if pf == pa:
        return False, "Points for and against cannot be equal for this match record."

    if data["result"] == "Win" and pf <= pa:
        return False, "A Win should have more points for than points against."

    if data["result"] == "Loss" and pf >= pa:
        return False, "A Loss should have fewer points for than points against."

    return True, ""


def normalize_match(data: Dict) -> Dict:
    """Convert form values into consistent storage types."""
    return {
        "id": str(data["id"]),
        "date": str(data["date"]).strip(),
        "opponent": str(data["opponent"]).strip(),
        "event": str(data["event"]).strip(),
        "result": str(data["result"]).strip(),
        "points_for": int(data["points_for"]),
        "points_against": int(data["points_against"]),
        "notes": str(data.get("notes", "")).strip(),
    }
