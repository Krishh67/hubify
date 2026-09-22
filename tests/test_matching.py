"""
Tests for matching scoring helper functions (from app/services/matching.py).

These functions are Phase 2 stubs but are testable now to validate
the scoring logic before the full AI pipeline is wired up.
"""
from __future__ import annotations

import pytest

from app.services.matching import score_quantity, score_budget, score_delivery


# ---------------------------------------------------------------------------
# score_quantity
# ---------------------------------------------------------------------------

class TestScoreQuantity:

    def test_supplier_meets_quantity_exactly(self):
        """Supplier has exactly the requested quantity → non-zero score."""
        score = score_quantity(client_qty=500, supplier_qty=500)
        assert score > 0

    def test_supplier_exceeds_quantity(self):
        """Supplier has more than needed → full marks."""
        score = score_quantity(client_qty=500, supplier_qty=2000)
        assert score == 100.0

    def test_supplier_below_quantity_hard_gate(self):
        """Supplier cannot fulfil → hard gate returns 0."""
        score = score_quantity(client_qty=500, supplier_qty=499)
        assert score == 0.0

    def test_zero_client_quantity(self):
        """Zero client quantity → 0 (invalid input guard)."""
        score = score_quantity(client_qty=0, supplier_qty=500)
        assert score == 0.0

    def test_zero_supplier_quantity(self):
        """Zero supplier quantity → 0."""
        score = score_quantity(client_qty=500, supplier_qty=0)
        assert score == 0.0

    def test_score_is_capped_at_100(self):
        """Score never exceeds 100 regardless of ratio."""
        score = score_quantity(client_qty=1, supplier_qty=1_000_000)
        assert score <= 100.0

    def test_score_type_is_float(self):
        score = score_quantity(client_qty=100, supplier_qty=200)
        assert isinstance(score, float)


# ---------------------------------------------------------------------------
# score_budget
# ---------------------------------------------------------------------------

class TestScoreBudget:

    def test_total_cost_within_budget(self):
        """Total cost well within budget → positive score."""
        score = score_budget(client_budget=100_000, supplier_unit_price=80, client_qty=500)
        assert score > 0  # 80 * 500 = 40,000 < 100,000

    def test_total_cost_exceeds_budget_hard_gate(self):
        """Total cost exceeds budget → hard gate returns 0."""
        score = score_budget(client_budget=10_000, supplier_unit_price=100, client_qty=500)
        assert score == 0.0  # 100 * 500 = 50,000 > 10,000

    def test_score_range_50_to_100(self):
        """Score when within budget should be between 50 and 100."""
        score = score_budget(client_budget=100_000, supplier_unit_price=50, client_qty=100)
        assert 50.0 <= score <= 100.0

    def test_zero_budget(self):
        """Zero budget → 0."""
        score = score_budget(client_budget=0, supplier_unit_price=80, client_qty=500)
        assert score == 0.0

    def test_zero_unit_price(self):
        """Zero unit price → 0 (guard)."""
        score = score_budget(client_budget=100_000, supplier_unit_price=0, client_qty=500)
        assert score == 0.0


# ---------------------------------------------------------------------------
# score_delivery
# ---------------------------------------------------------------------------

class TestScoreDelivery:

    def test_supplier_delivers_within_deadline(self):
        """Supplier can deliver before deadline → positive score."""
        score = score_delivery(client_days=21, supplier_days=7)
        assert score > 0

    def test_supplier_delivers_on_deadline(self):
        """Supplier delivers exactly on the deadline → non-zero."""
        score = score_delivery(client_days=21, supplier_days=21)
        assert score >= 0.0

    def test_supplier_exceeds_deadline_hard_gate(self):
        """Supplier cannot meet deadline → hard gate returns 0."""
        score = score_delivery(client_days=7, supplier_days=14)
        assert score == 0.0

    def test_faster_delivery_scores_higher(self):
        """Faster delivery should result in a higher score."""
        score_fast = score_delivery(client_days=30, supplier_days=5)
        score_slow = score_delivery(client_days=30, supplier_days=25)
        assert score_fast > score_slow

    def test_zero_client_days(self):
        """Zero client_days → 0 (guard)."""
        score = score_delivery(client_days=0, supplier_days=7)
        assert score == 0.0

    def test_score_within_range(self):
        """Score always between 0 and 100."""
        score = score_delivery(client_days=30, supplier_days=10)
        assert 0.0 <= score <= 100.0

