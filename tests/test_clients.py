"""
Tests for POST /api/clients and GET /api/clients endpoints.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from tests.conftest import VALID_CLIENT


# ---------------------------------------------------------------------------
# POST /api/clients
# ---------------------------------------------------------------------------

def test_create_client_valid(client):
    """Valid client payload → 201 with returned record including int id."""
    fake_record = {**VALID_CLIENT, "id": 1, "created_at": "2026-09-22T08:00:00+00:00"}

    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.insert.return_value.execute.return_value.data = [fake_record]
        response = client.post("/api/clients", json=VALID_CLIENT)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["client_name"] == VALID_CLIENT["client_name"]
    assert body["email"] == VALID_CLIENT["email"]
    assert isinstance(body["id"], int)  # BIGINT — must be int, not string


def test_create_client_missing_required_field(client):
    """Missing client_name → 422 Unprocessable Entity."""
    payload = {**VALID_CLIENT}
    del payload["client_name"]
    response = client.post("/api/clients", json=payload)
    assert response.status_code == 422


def test_create_client_invalid_email(client):
    """Invalid email format → 422."""
    payload = {**VALID_CLIENT, "email": "not-an-email"}
    response = client.post("/api/clients", json=payload)
    assert response.status_code == 422


def test_create_client_zero_quantity(client):
    """quantity_required = 0 violates gt=0 constraint → 422."""
    payload = {**VALID_CLIENT, "quantity_required": 0}
    response = client.post("/api/clients", json=payload)
    assert response.status_code == 422


def test_create_client_negative_quantity(client):
    """Negative quantity → 422."""
    payload = {**VALID_CLIENT, "quantity_required": -10}
    response = client.post("/api/clients", json=payload)
    assert response.status_code == 422


def test_create_client_negative_budget(client):
    """Negative budget → 422."""
    payload = {**VALID_CLIENT, "budget": -1}
    response = client.post("/api/clients", json=payload)
    assert response.status_code == 422


def test_create_client_zero_delivery_days(client):
    """delivery_days = 0 violates gt=0 → 422."""
    payload = {**VALID_CLIENT, "delivery_days": 0}
    response = client.post("/api/clients", json=payload)
    assert response.status_code == 422


def test_create_client_optional_fields_nullable(client):
    """Optional fields (additional_notes, specs, certifications) may be None → 201."""
    payload = {
        **VALID_CLIENT,
        "additional_notes": None,
        "specs": None,
        "certifications": None,
    }
    fake_record = {**payload, "id": 2, "created_at": "2026-09-22T08:00:00+00:00"}

    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.insert.return_value.execute.return_value.data = [fake_record]
        response = client.post("/api/clients", json=payload)

    assert response.status_code == 201


# ---------------------------------------------------------------------------
# GET /api/clients
# ---------------------------------------------------------------------------

def test_get_clients_returns_list(client):
    """GET /api/clients → 200 with a list."""
    fake_records = [
        {**VALID_CLIENT, "id": 1, "created_at": "2026-09-22T08:00:00+00:00"},
        {**VALID_CLIENT, "id": 2, "client_name": "Corp Two", "created_at": "2026-09-22T09:00:00+00:00"},
    ]

    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = fake_records
        response = client.get("/api/clients")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id"] == 1
    assert body[1]["id"] == 2


def test_get_clients_empty_database(client):
    """GET /api/clients with empty DB → 200 with empty list."""
    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value.data = []
        response = client.get("/api/clients")

    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /api/clients/{id}
# ---------------------------------------------------------------------------

def test_get_client_by_id_found(client):
    """GET /api/clients/1 → 200 with single record."""
    fake_record = {**VALID_CLIENT, "id": 1, "created_at": "2026-09-22T08:00:00+00:00"}

    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [fake_record]
        response = client.get("/api/clients/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_client_by_id_not_found(client):
    """GET /api/clients/9999 when no record exists → 404."""
    with patch("app.services.database.supabase") as mock_sb:
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        response = client.get("/api/clients/9999")

    assert response.status_code == 404

