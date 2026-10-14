"""
analytics.py
Pandas/NumPy based performance calculations and chart preparation.
"""

from typing import Dict, List
import numpy as np
import pandas as pd


def matches_dataframe(matches: List[Dict]) -> pd.DataFrame:
    """Convert match dictionaries to a clean pandas DataFrame."""
    columns = [
        "id", "date", "opponent", "event", "result",
        "points_for", "points_against", "notes"
    ]
    if not matches:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(matches)
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    df["points_for"] = pd.to_numeric(df["points_for"], errors="coerce").fillna(0).astype(int)
    df["points_against"] = pd.to_numeric(df["points_against"], errors="coerce").fillna(0).astype(int)
    return df[columns].sort_values("date", ascending=False).reset_index(drop=True)


def calculate_statistics(matches: List[Dict]) -> Dict:
    """Calculate win/loss and scoring statistics using NumPy/Pandas."""
    df = matches_dataframe(matches)
    total = len(df)
    if total == 0:
        return {
            "total": 0, "wins": 0, "losses": 0, "win_rate": 0.0,
            "points_for": 0, "points_against": 0, "avg_for": 0.0,
            "avg_against": 0.0, "best_margin": 0, "worst_margin": 0
        }

    wins = int((df["result"] == "Win").sum())
    losses = int((df["result"] == "Loss").sum())
    pf = df["points_for"].to_numpy(dtype=float)
    pa = df["points_against"].to_numpy(dtype=float)
    margins = pf - pa

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round((wins / total) * 100, 1),
        "points_for": int(np.sum(pf)),
        "points_against": int(np.sum(pa)),
        "avg_for": round(float(np.mean(pf)), 1),
        "avg_against": round(float(np.mean(pa)), 1),
        "best_margin": int(np.max(margins)),
        "worst_margin": int(np.min(margins)),
    }


def opponent_summary(matches: List[Dict]) -> pd.DataFrame:
    """Return wins/losses and win rate grouped by opponent."""
    df = matches_dataframe(matches)
    if df.empty:
        return pd.DataFrame(columns=["opponent", "matches", "wins", "losses", "win_rate"])
    grouped = df.groupby("opponent", as_index=False).agg(
        matches=("id", "count"),
        wins=("result", lambda s: int((s == "Win").sum())),
        losses=("result", lambda s: int((s == "Loss").sum())),
    )
    grouped["win_rate"] = (grouped["wins"] / grouped["matches"] * 100).round(1)
    return grouped.sort_values(["win_rate", "matches"], ascending=[False, False])


def event_summary(matches: List[Dict]) -> pd.DataFrame:
    """Return performance grouped by event/tournament."""
    df = matches_dataframe(matches)
    if df.empty:
        return pd.DataFrame(columns=["event", "matches", "wins", "losses", "win_rate"])
    grouped = df.groupby("event", as_index=False).agg(
        matches=("id", "count"),
        wins=("result", lambda s: int((s == "Win").sum())),
        losses=("result", lambda s: int((s == "Loss").sum())),
    )
    grouped["win_rate"] = (grouped["wins"] / grouped["matches"] * 100).round(1)
    return grouped.sort_values("win_rate", ascending=False)


def recent_form(matches: List[Dict], count: int = 5) -> str:
    """Return the most recent results as a compact form string."""
    df = matches_dataframe(matches)
    if df.empty:
        return "No matches"
    results = df.sort_values("date", ascending=False)["result"].head(count).tolist()
    return " - ".join("W" if r == "Win" else "L" for r in results)


def export_dataframe(matches: List[Dict]) -> pd.DataFrame:
    """Prepare a user-friendly DataFrame for CSV export."""
    df = matches_dataframe(matches).copy()
    if not df.empty:
        df.insert(0, "Player", "Naitik Parmar")
        df["score"] = df["points_for"].astype(str) + " - " + df["points_against"].astype(str)
    return df
