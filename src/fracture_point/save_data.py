from __future__ import annotations

import json
from pathlib import Path

from fracture_point.item import Item

SAVE_PATH = Path("saves")/"save.json"
DEFAULT_SAVE = {
    "currency": 0,
    "gear":{"equipped": {}, "inventory": []},
    }

def _item_to_dict(item: Item) -> dict:
    return{
        "name": item.name,
        "char": item.char,
        "color": list(item.color),
        "slot_types": list(item.slot_types),
        "power_bonus": item.power_bonus,
        "defense_bonus": item.defense_bonus,
    }

def _item_from_dict(data: dict) -> Item:
    return Item(
        name=data["name"],
        char=data["char"],
        color=tuple(data["color"]),
        slot_types=list(data["slot_types"]),
        power_bonus=data["power_bonus"],
        defense_bonus=data["defense_bonus"],
    )
 
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

def _write(data: dict) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def save_currency(amount: int)->None:
    data = load_save()
    data["currency"] = amount
    _write(data)

def save_gear(equipped: dict[str, Item | None], inventory_items: list[Item]) -> None:
    """
    Called on a successful floor completion: banks whatever player is currently wearing/carrying so it's available in the hub (when that's created).
    """
    data = load_save()
    data["gear"] = {
        "equipped":{
            slot_id: _item_to_dict(item) for slot_id, item in equipped.items() if item is not None
        },
        "inventory":[_item_to_dict(item) for item in inventory_items],
    }
    _write(data)

def clear_gains() -> None:
    """
    Called on death: wipes inventory, equipped, and currency upon death. May alter this when hub is added.
    """
    data = load_save()
    data = DEFAULT_SAVE

def load_gear() -> tuple[dict[str, Item], list[Item]]:
    """
    Returns (equipped_by_slot, inventory_items) reconstructed from the save file. Empty dict/list if nothing was ever saved.
    """
    data = load_save()
    equipped = {
        slot_id: _item_from_dict(item_data) for slot_id, item_data in data["gear"]["equipped"].items()
    }
    inventory_items = [_item_from_dict(item_data) for item_data in data["gear"]["inventory"]]
    return equipped, inventory_items