from __future__ import annotations

import json
import random
from pathlib import Path

from fracture_point.consumable import Consumable
from fracture_point.entity import Entity
from fracture_point.gem import Gem
from fracture_point.item import Item

"""
Loads the loot pool from data/loot_table.json.

The JSON is organized into named sections: "items" is further split 
into "weapons", "rings", "wands", etc.; "gems" and "consumables". Which section an entry lives in determines its type - you don't need to (and shouldn't) repeat a "type" field inside
each entry.

To add a new droppable item: drop a new object into the matching
section (or add a new sub-section under "items" for a slot category
that doesn't exist yet - update ITEM_SECTIONS below if so). Nothing
else in this file needs to change.

Entry fields:
  All types: "name", "char", "color", "weight" (relative drop chance -
             higher = more common, no need to sum to anything).
  Item entries: slot_types, power_bonus, magic_power_bonus,
             defense_bonus, gem_slots, base_name, identify_property,
             and optionally "socketed_gem" (a nested gem dict, same
             shape as a gem entry minus "weight") for items that spawn
             pre-socketed.
  Gem entries: max_charge, charge_per_turn, cast_cost.
  Consumable entries: kind.
"""

DATA_PATH = Path(__file__).parent / "data" / "loot_table.json"

# Every key expected under the "items" section. If you add a new item
# sub-section to the JSON, add its name here too, or it
# won't get picked up by the loader.
ITEM_SECTIONS = ["weapons", "rings", "wands"]


def _build_gem(data: dict) -> Gem:
    return Gem(
        name=data["name"],
        char=data["char"],
        color=tuple(data["color"]),
        max_charge=data["max_charge"],
        charge_per_turn=data["charge_per_turn"],
        cast_cost=data["cast_cost"],
    )


def _build_item_entity(data: dict, x: int, y: int) -> Entity:
    gem_slots = data.get("gem_slots", 0)
    sockets = [None] * gem_slots

    socketed_gem_data = data.get("socketed_gem")
    if socketed_gem_data is not None and gem_slots > 0:
        sockets[0] = _build_gem(socketed_gem_data)

    item = Item(
        name=data["name"],
        char=data["char"],
        color=tuple(data["color"]),
        slot_types=list(data.get("slot_types", ["weapon"])),
        power_bonus=data.get("power_bonus", 0),
        magic_power_bonus=data.get("magic_power_bonus", 0),
        defense_bonus=data.get("defense_bonus", 0),
        gem_slots=gem_slots,
        sockets=sockets,
        base_name=data.get("base_name", ""),
        identify_property=data.get("identify_property"),
    )
    return Entity(x=x, y=y, char=data["char"], color=tuple(data["color"]), name=data["name"], item=item)


def _build_gem_entity(data: dict, x: int, y: int) -> Entity:
    gem = _build_gem(data)
    return Entity(x=x, y=y, char=data["char"], color=tuple(data["color"]), name=data["name"], gem=gem)


def _build_consumable_entity(data: dict, x: int, y: int) -> Entity:
    consumable = Consumable(name=data["name"], char=data["char"], color=tuple(data["color"]), kind=data["kind"])
    return Entity(x=x, y=y, char=data["char"], color=tuple(data["color"]), name=data["name"], consumable=consumable)


def load_loot_entries(path: Path = DATA_PATH) -> list[tuple[dict, callable]]:
    """
    Flattens the sectioned JSON into a single list of (entry, builder)
    pairs, ready for weighted random selection. Each entry keeps its
    original dict; the builder is just which _build_* function applies,
    determined by which section it came from.
    """
    with open(path, "r") as f:
        data = json.load(f)

    flattened: list[tuple[dict, callable]] = []

    for section_name in ITEM_SECTIONS:
        for entry in data.get("items", {}).get(section_name, []):
            flattened.append((entry, _build_item_entity))

    for entry in data.get("gems", []):
        flattened.append((entry, _build_gem_entity))

    for entry in data.get("consumables", []):
        flattened.append((entry, _build_consumable_entity))

    return flattened


# Loaded once at import time. If you're editing the JSON while the
# game is running, you'll need to restart to see changes.
_LOOT_ENTRIES = load_loot_entries()


def pick_loot(x: int, y: int) -> Entity:
    """Picks one random loot entry, weighted by its 'weight' field, and
    builds a fresh Entity for it at (x, y)."""
    weights = [entry["weight"] for entry, _builder in _LOOT_ENTRIES]
    entry, builder = random.choices(_LOOT_ENTRIES, weights=weights, k=1)[0]
    return builder(entry, x, y)