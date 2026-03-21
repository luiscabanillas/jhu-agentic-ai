"""Inventory and cart helpers for the Week 1 AI inventory exercise."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    item_id: int
    name: str
    price: int


INVENTORY: list[Item] = [
    Item(101, "Hammer", 120),
    Item(102, "Screwdriver Set", 350),
    Item(103, "Drill Machine", 2500),
    Item(104, "Pliers", 180),
    Item(105, "Wrench", 220),
]


INVENTORY_BY_ID = {item.item_id: item for item in INVENTORY}


def inventory_choices() -> list[tuple[str, int]]:
    """Return label/value pairs for Gradio dropdowns."""
    return [
        (f"{item.item_id} - {item.name} (${item.price})", item.item_id)
        for item in INVENTORY
    ]


def cart_choices(cart: list[int]) -> list[tuple[str, int]]:
    choices: list[tuple[str, int]] = []
    for index, item_id in enumerate(cart):
        item = INVENTORY_BY_ID[item_id]
        choices.append(
            (f"{index + 1}. {item.item_id} - {item.name} (${item.price})", index)
        )
    return choices


def add_to_cart(item_id: int | None, cart: list[int]) -> tuple[list[int], str]:
    if item_id is None:
        return cart, "Select an inventory item before adding it to the cart."

    if item_id not in INVENTORY_BY_ID:
        return cart, f"Item ID {item_id} is not in the inventory."

    updated_cart = [*cart, item_id]
    item = INVENTORY_BY_ID[item_id]
    return updated_cart, f"Added {item.name} (${item.price}) to the cart."


def remove_from_cart(cart_index: int | None, cart: list[int]) -> tuple[list[int], str]:
    if cart_index is None:
        return cart, "Select a cart item before removing it."

    if cart_index < 0 or cart_index >= len(cart):
        return cart, "The selected cart item no longer exists."

    updated_cart = cart.copy()
    removed_id = updated_cart.pop(cart_index)
    item = INVENTORY_BY_ID[removed_id]
    return updated_cart, f"Removed {item.name} (${item.price}) from the cart."


def calculate_total(cart: list[int]) -> int:
    return sum(INVENTORY_BY_ID[item_id].price for item_id in cart)


def render_cart(cart: list[int]) -> str:
    if not cart:
        return "Cart is empty."

    lines = []
    for index, item_id in enumerate(cart, start=1):
        item = INVENTORY_BY_ID[item_id]
        lines.append(f"{index}. {item.name} (ID: {item.item_id}) - ${item.price}")
    return "\n".join(lines)
