"""Tests for inventory_tracker module."""

from __future__ import annotations

from scripts.inventory_tracker import (
    add_stock,
    low_stock_alert,
    merge_inventories,
    reconcile,
)


class TestAddStock:
    """Tests for add_stock function."""

    def test_add_new_warehouse(self) -> None:
        inv: dict[str, dict[str, int]] = {}
        result = add_stock(inv, "WH-A", "SKU-1", 100)
        assert result == {"WH-A": {"SKU-1": 100}}

    def test_add_sku_to_existing_warehouse(self) -> None:
        inv: dict[str, dict[str, int]] = {"WH-A": {"SKU-1": 100}}
        result = add_stock(inv, "WH-A", "SKU-2", 50)
        assert result == {"WH-A": {"SKU-1": 100, "SKU-2": 50}}

    def test_update_existing_sku(self) -> None:
        inv: dict[str, dict[str, int]] = {"WH-A": {"SKU-1": 100}}
        result = add_stock(inv, "WH-A", "SKU-1", 200)
        assert result == {"WH-A": {"SKU-1": 200}}


class TestReconcile:
    """Tests for reconcile function — single warehouse scenarios."""

    def test_no_discrepancies(self) -> None:
        inv = {"WH-A": {"SKU-1": 100, "SKU-2": 50}}
        expected = {"WH-A": {"SKU-1": 100, "SKU-2": 50}}
        assert reconcile(inv, expected) == []

    def test_qty_mismatch(self) -> None:
        inv = {"WH-A": {"SKU-1": 100}}
        expected = {"WH-A": {"SKU-1": 80}}
        result = reconcile(inv, expected)
        assert result == [("WH-A", "SKU-1", 100, 80)]

    def test_missing_sku(self) -> None:
        inv = {"WH-A": {"SKU-1": 100}}
        expected = {"WH-A": {"SKU-1": 100, "SKU-2": 50}}
        result = reconcile(inv, expected)
        assert result == [("WH-A", "SKU-2", 0, 50)]

    def test_multiple_warehouses(self) -> None:
        inv = {"WH-A": {"SKU-1": 100}, "WH-B": {"SKU-1": 80}}
        expected = {"WH-A": {"SKU-1": 100}, "WH-B": {"SKU-1": 100}}
        result = reconcile(inv, expected)
        assert result == [("WH-B", "SKU-1", 80, 100)]


class TestMergeInventories:
    """Tests for merge_inventories function."""

    def test_disjoint_warehouses(self) -> None:
        inv1 = {"WH-A": {"SKU-1": 100}}
        inv2 = {"WH-B": {"SKU-2": 50}}
        result = merge_inventories(inv1, inv2)
        assert result == {"WH-A": {"SKU-1": 100}, "WH-B": {"SKU-2": 50}}

    def test_same_warehouse_overwrite(self) -> None:
        inv1 = {"WH-A": {"SKU-1": 100, "SKU-2": 50}}
        inv2 = {"WH-A": {"SKU-1": 80}}
        result = merge_inventories(inv1, inv2)
        assert result == {"WH-A": {"SKU-1": 80, "SKU-2": 50}}


class TestLowStockAlert:
    """Tests for low_stock_alert function."""

    def test_below_threshold(self) -> None:
        inv = {"WH-A": {"SKU-1": 5, "SKU-2": 50}}
        result = low_stock_alert(inv, 10)
        assert result == [("WH-A", "SKU-1", 5)]

    def test_no_alerts(self) -> None:
        inv = {"WH-A": {"SKU-1": 100}}
        result = low_stock_alert(inv, 10)
        assert result == []
