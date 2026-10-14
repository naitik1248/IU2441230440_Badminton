"""
storage.py
Persistent JSON file handling for the Badminton Match Performance Analyzer.
"""

import json
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).with_name("matches.json")


def load_matches() -> List[Dict]:
    """Load all match records from JSON storage."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_matches(matches: List[Dict]) -> None:
    """Save all match records to JSON storage."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(matches, file, indent=4, ensure_ascii=False)


def add_match(match: Dict) -> List[Dict]:
    """Add one match and persist it."""
    matches = load_matches()
    matches.append(match)
    save_matches(matches)
    return matches


def update_match(match_id: str, updated: Dict) -> List[Dict]:
    """Update a match by its unique ID."""
    matches = load_matches()
    for index, match in enumerate(matches):
        if match.get("id") == match_id:
            matches[index] = updated
            break
    save_matches(matches)
    return matches


def delete_match(match_id: str) -> List[Dict]:
    """Delete a match by its unique ID."""
    matches = [m for m in load_matches() if m.get("id") != match_id]
    save_matches(matches)
    return matches
