from __future__ import annotations

import json
from pathlib import Path

from fracture_point.gem import Gem
from fracture_point.item import Item

SAVE_PATH = Path("saves") / "save.json"

DEFAULT_SAVE = {
    "currency": 0,
    "gear": {"equipped": {}, "inventory": []},
}


def _gem_to_dict(gem: Gem) -> dict:
    return {
        "name": gem.name,
        "char": gem.char,
        "color": list(gem.color),
        "max_charge": gem.max_charge,
        "charge_per_turn": gem.charge_per_turn,
        "cast_cost": gem.cast_cost,
        "current_charge": gem.current_charge,
    }


def _gem_from_dict(data: dict) -> Gem:
    return Gem(
        name=data["name"],
        char=data["char"],
        color=tuple(data["color"]),
        max_charge=data["max_charge"],
        charge_per_turn=data["charge_per_turn"],
        cast_cost=data["cast_cost"],
        current_charge=data["current_charge"],
    )


def _item_to_dict(item: Item) -> dict:
    return {
        "name": item.name,
        "char": item.char,
        "color": list(item.color),
        "slot_types": list(item.slot_types),
        "power_bonus": item.power_bonus,
        "magic_power_bonus": item.magic_power_bonus,
        "defense_bonus": item.defense_bonus,
        "gem_slots": item.gem_slots,
        "sockets": [(_gem_to_dict(g) if g is not None else None) for g in item.sockets],
    }


def _item_from_dict(data: dict) -> Item:
    gem_slots = data.get("gem_slots", 0)
    sockets_data = data.get("sockets", [None] * gem_slots)
    sockets = [(_gem_from_dict(g) if g is not None else None) for g in sockets_data]

    return Item(
        name=data["name"],
        char=data["char"],
        color=tuple(data["color"]),
        slot_types=list(data["slot_types"]),
        power_bonus=data["power_bonus"],
        magic_power_bonus=data.get("magic_power_bonus", 0),
        defense_bonus=data["defense_bonus"],
        gem_slots=gem_slots,
        sockets=sockets,
    )


def load_save() -> dict:
    if not SAVE_PATH.exists():
        return json.loads(json.dumps(DEFAULT_SAVE))
    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(DEFAULT_SAVE))

    merged = json.loads(json.dumps(DEFAULT_SAVE))
    merged.update(data)
    return merged


def _write(data: dict) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def save_currency(amount: int) -> None:
    data = load_save()
    data["currency"] = amount
    _write(data)


def save_gear(equipped: dict[str, Item | None], inventory_items: list[Item]) -> None:
    data = load_save()
    data["gear"] = {
        "equipped": {
            slot_id: _item_to_dict(item) for slot_id, item in equipped.items() if item is not None
        },
        "inventory": [_item_to_dict(item) for item in inventory_items],
    }
    _write(data)


def clear_gear() -> None:
    data = load_save()
    data["gear"] = {"equipped": {}, "inventory": []}
    _write(data)


def load_gear() -> tuple[dict[str, Item], list[Item]]:
    data = load_save()
    equipped = {
        slot_id: _item_from_dict(item_data)
        for slot_id, item_data in data["gear"]["equipped"].items()
    }
    inventory_items = [_item_from_dict(item_data) for item_data in data["gear"]["inventory"]]
    return equipped, inventory_items