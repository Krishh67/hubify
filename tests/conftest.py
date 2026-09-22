"""
Pytest configuration and fixtures.

Uses FastAPI's TestClient with mocked Supabase calls so unit tests
do not hit the real database.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def mock_settings():
    """Provide fake env values so config.validate() passes during tests."""
    with patch("app.config.settings") as mock:
        mock.SUPABASE_URL = "https://fake.supabase.co"
        mock.SUPABASE_KEY = "fake-key"
        mock.GEMINI_API_KEY = "fake-gemini-key"
        mock.validate = lambda: None
        yield mock


@pytest.fixture(scope="session")
def client(mock_settings):
    """FastAPI TestClient with Supabase calls mocked at the service layer."""
    with patch("app.services.database.supabase") as mock_supabase:
        # Default mock behaviour — most tests override this per call
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = []

        from app.main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ---------------------------------------------------------------------------
# Sample payloads
# ---------------------------------------------------------------------------

VALID_CLIENT = {
    "client_name":         "Test Corp",
    "email":               "test@testcorp.com",
    "product_requirement": "High-grade stainless steel sheets",
    "category":            "Raw Materials",
    "quantity_required":   500.0,
    "unit":                "Kilograms (kg)",
    "budget":              250000.0,
    "location":            "Industrial Zone, Navi Mumbai",
    "city":                "Mumbai",
    "state":               "Maharashtra",
    "country":             "India",
    "delivery_timeline":   "Within 3 weeks",
    "delivery_days":       21,
    "additional_notes":    None,
    "specs":               "Grade 304, 2mm thickness",
    "certifications":      "ISO 9001",
}

VALID_SUPPLIER = {
    "supplier_name":      "Steel Suppliers Ltd",
    "email":              "info@steelsuppliers.com",
    "product_offered":    "Stainless Steel Sheets Grade 304",
    "category":           "Raw Materials",
    "available_quantity": 10000.0,
    "unit":               "Kilograms (kg)",
    "pricing_details":    "₹80/kg for orders above 200kg",
    "unit_price":         80.0,
    "min_order_qty":      200.0,
    "location":           "GIDC, Vatva",
    "city":               "Ahmedabad",
    "state":              "Gujarat",
    "country":            "India",
    "delivery_capability":"Pan-India, 7-day standard",
    "delivery_days":      7,
    "additional_notes":   None,
    "specs":              "Grade 304, various thicknesses",
    "certifications":     "ISO 9001:2015",
}

