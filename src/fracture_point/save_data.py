from __future__ import annotations

import json
from pathlib import Path

SAVE_PATH = Path("saves")/"save.json"
DEFAULT_SAVE = {"currency": 0}

def load_save() -> dict:
    """
    Loads persistent meta-progression data. Currently just currency, but will later add recipes, materials, etc. Returns defaults if no save exists yet (first-ever run).
    """

    if not SAVE_PATH.exists():
        return dict(DEFAULT_SAVE)
    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
    except(json.JSONDecodeError, OSError):
        return dict(DEFAULT_SAVE)
    return{**DEFAULT_SAVE, **data}

def save_currency(amount: int)->None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = load_save()
    data["currency"] = amount
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)