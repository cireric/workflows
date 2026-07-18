"""Inventory tracking tools for multi-warehouse stock management."""

from __future__ import annotations


def add_stock(
    inventory: dict[str, dict[str, int]], warehouse: str, sku: str, qty: int
) -> dict[str, dict[str, int]]:
    """Add or update stock quantity for a SKU in a warehouse.

    Args:
        inventory: Nested dict mapping warehouse name to {sku: qty}.
        warehouse: Warehouse identifier.
        sku: Stock-keeping unit identifier.
        qty: Quantity to set (replaces existing value, does not add).

    Returns:
        Updated inventory dict.
    """
    if warehouse not in inventory:
        inventory[warehouse] = {}
    inventory[warehouse][sku] = qty
    return inventory


def reconcile(
    inventory: dict[str, dict[str, int]], expected: dict[str, dict[str, int]]
) -> list[tuple[str, str, int, int]]:
    """Find discrepancies between actual and expected stock per warehouse.

    Checks each warehouse independently: for every SKU present in a
    warehouse's expected counts, compares with actual quantity.

    Args:
        inventory: Actual stock levels, {warehouse: {sku: qty}}.
        expected: Expected stock levels, same structure.

    Returns:
        List of (warehouse, sku, actual_qty, expected_qty) tuples where
        actual != expected.
    """
    discrepancies: list[tuple[str, str, int, int]] = []
    for wh, skus in expected.items():
        for sku, exp_qty in skus.items():
            act_qty = inventory.get(wh, {}).get(sku, 0)
            if act_qty != exp_qty:
                discrepancies.append((wh, sku, act_qty, exp_qty))
    return discrepancies


def merge_inventories(
    inv1: dict[str, dict[str, int]], inv2: dict[str, dict[str, int]]
) -> dict[str, dict[str, int]]:
    """Merge two inventories, keeping all warehouse entries.

    If the same warehouse appears in both inventories, SKUs from inv2
    overwrite those from inv1 for that warehouse. SKUs unique to each
    inventory are preserved.

    Args:
        inv1: First inventory.
        inv2: Second inventory.

    Returns:
        Merged inventory dict.
    """
    merged: dict[str, dict[str, int]] = {}
    for wh, skus in inv1.items():
        merged[wh] = dict(skus)
    for wh, skus in inv2.items():
        if wh in merged:
            merged[wh].update(skus)
        else:
            merged[wh] = dict(skus)
    return merged


def low_stock_alert(
    inventory: dict[str, dict[str, int]], threshold: int
) -> list[tuple[str, str, int]]:
    """Find all SKU entries below the given threshold.

    Args:
        inventory: Stock levels, {warehouse: {sku: qty}}.
        threshold: Quantity below which an alert is generated.

    Returns:
        List of (warehouse, sku, qty) tuples where qty < threshold.
    """
    alerts: list[tuple[str, str, int]] = []
    for wh, skus in inventory.items():
        for sku, qty in skus.items():
            if qty < threshold:
                alerts.append((wh, sku, qty))
    return alerts
