"""
Tests for POST /api/suppliers and GET /api/suppliers endpoints.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from tests.conftest import VALID_SUPPLIER


# ---------------------------------------------------------------------------
# POST /api/suppliers
# ---------------------------------------------------------------------------

def test_create_supplier_valid(client):
    """Valid supplier payload → 201 with returned record including int id."""
    fake_record = {**VALID_SUPPLIER, "id": 1, "created_at": "2026-09-22T08:00:00+00:00"}

    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.insert.return_value.execute.return_value.data = [fake_record]
        response = client.post("/api/suppliers", json=VALID_SUPPLIER)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["supplier_name"] == VALID_SUPPLIER["supplier_name"]
    assert isinstance(body["id"], int)  # BIGINT — must be int


def test_create_supplier_missing_required_field(client):
    """Missing supplier_name → 422."""
    payload = {**VALID_SUPPLIER}
    del payload["supplier_name"]
    response = client.post("/api/suppliers", json=payload)
    assert response.status_code == 422


def test_create_supplier_invalid_email(client):
    """Invalid email → 422."""
    payload = {**VALID_SUPPLIER, "email": "bad-email"}
    response = client.post("/api/suppliers", json=payload)
    assert response.status_code == 422


def test_create_supplier_negative_unit_price(client):
    """unit_price < 0 → 422."""
    payload = {**VALID_SUPPLIER, "unit_price": -5}
    response = client.post("/api/suppliers", json=payload)
    assert response.status_code == 422


def test_create_supplier_zero_delivery_days(client):
    """delivery_days = 0 → 422."""
    payload = {**VALID_SUPPLIER, "delivery_days": 0}
    response = client.post("/api/suppliers", json=payload)
    assert response.status_code == 422


def test_create_supplier_missing_pricing_details(client):
    """Missing pricing_details → 422."""
    payload = {**VALID_SUPPLIER}
    del payload["pricing_details"]
    response = client.post("/api/suppliers", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/suppliers
# ---------------------------------------------------------------------------

def test_get_suppliers_returns_list(client):
    """GET /api/suppliers → 200 with list."""
    fake_records = [
        {**VALID_SUPPLIER, "id": 1, "created_at": "2026-09-22T08:00:00+00:00"},
        {**VALID_SUPPLIER, "id": 2, "supplier_name": "Another Supplier", "created_at": "2026-09-22T09:00:00+00:00"},
    ]

    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = fake_records
        response = client.get("/api/suppliers")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


def test_get_suppliers_empty(client):
    """GET /api/suppliers empty DB → 200, empty list."""
    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = []
        response = client.get("/api/suppliers")

    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /api/suppliers/{id}
# ---------------------------------------------------------------------------

def test_get_supplier_by_id_found(client):
    """GET /api/suppliers/1 → 200."""
    fake_record = {**VALID_SUPPLIER, "id": 1, "created_at": "2026-09-22T08:00:00+00:00"}

    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [fake_record]
        response = client.get("/api/suppliers/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_supplier_by_id_not_found(client):
    """GET /api/suppliers/9999 → 404."""
    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        response = client.get("/api/suppliers/9999")

    assert response.status_code == 404

