"""
test_sprint31_functional.py — Functional tests for Sprint 31.

Sprint 31 adds ClusterSidebar — a left panel with cluster cards in «По районам» mode.
- Shows all clusters as cards with ST count, pallet count, weight.
- Clicking a card toggles expand/collapse in the main table.
- «⚡ Рейс» button on each card opens ClusterQuickCreateDialog.
- Total summary in sidebar header.

Backend: no new endpoints — purely frontend sprint.
Tests focus on cluster aggregation math (sidebar totals).
"""

import pytest


# ---------------------------------------------------------------------------
# Sidebar total aggregation logic
# ---------------------------------------------------------------------------

def sidebar_totals(clusters: list[dict]) -> dict:
    """Mirror of ClusterSidebar reduce logic."""
    return {
        "raion_count": len(clusters),
        "st_total": sum(c["ST_COUNT"] for c in clusters),
        "pallet_total": sum(c["PALLET_COUNT"] for c in clusters),
        "weight_total": sum(c["WEIGHT_KG"] for c in clusters),
    }


class TestClusterSidebarTotals:

    def test_empty_clusters(self):
        t = sidebar_totals([])
        assert t["raion_count"] == 0
        assert t["st_total"] == 0

    def test_single_cluster(self):
        t = sidebar_totals([{"RAION": "Север", "ST_COUNT": 3, "PALLET_COUNT": 10, "WEIGHT_KG": 400.0}])
        assert t["raion_count"] == 1
        assert t["st_total"] == 3
        assert t["pallet_total"] == 10
        assert t["weight_total"] == 400.0

    def test_multiple_clusters_sum(self):
        clusters = [
            {"RAION": "Север",  "ST_COUNT": 3, "PALLET_COUNT": 10, "WEIGHT_KG": 400.0},
            {"RAION": "Юг",     "ST_COUNT": 5, "PALLET_COUNT": 20, "WEIGHT_KG": 800.0},
            {"RAION": "Восток", "ST_COUNT": 2, "PALLET_COUNT": 6,  "WEIGHT_KG": 200.0},
        ]
        t = sidebar_totals(clusters)
        assert t["raion_count"] == 3
        assert t["st_total"] == 10
        assert t["pallet_total"] == 36
        assert t["weight_total"] == pytest.approx(1400.0)

    def test_no_raion_cluster_included(self):
        clusters = [
            {"RAION": "(без района)", "ST_COUNT": 4, "PALLET_COUNT": 8, "WEIGHT_KG": 300.0},
        ]
        t = sidebar_totals(clusters)
        assert t["raion_count"] == 1
        assert t["st_total"] == 4


# ---------------------------------------------------------------------------
# Cluster data integrity (backend regression)
# ---------------------------------------------------------------------------

class TestClusterDataIntegrity:

    def test_cluster_fields_present(self):
        """All required cluster fields must be present for sidebar rendering."""
        from unittest.mock import patch
        from app.services.transport_service import TransportService
        from datetime import date

        sts = [
            {"ST_NUMBER": "S1", "RAION": "Север", "PALLETS_COUNT": 3, "WEIGHT_KG": 100.0, "VOLUME_M3": 0.5},
        ]
        svc = TransportService()
        with patch.object(svc, "list_available_sts", return_value=sts):
            result = svc.list_clusters(stdate=date.today())

        assert len(result) == 1
        c = result[0]
        for field in ("RAION", "ST_COUNT", "PALLET_COUNT", "WEIGHT_KG", "VOLUME_M3", "STS"):
            assert field in c, f"Missing field {field} in cluster dict"

    def test_clusters_sorted_alphabetically_no_raion_last(self):
        """Clusters sorted alphabetically; «(без района)» always last."""
        from unittest.mock import patch
        from app.services.transport_service import TransportService
        from datetime import date

        sts = [
            {"ST_NUMBER": "S1", "RAION": None,      "PALLETS_COUNT": 1, "WEIGHT_KG": 50.0, "VOLUME_M3": 0.1},
            {"ST_NUMBER": "S2", "RAION": "Юг",      "PALLETS_COUNT": 5, "WEIGHT_KG": 200.0, "VOLUME_M3": 1.0},
            {"ST_NUMBER": "S3", "RAION": "Север",   "PALLETS_COUNT": 3, "WEIGHT_KG": 150.0, "VOLUME_M3": 0.8},
        ]
        svc = TransportService()
        with patch.object(svc, "list_available_sts", return_value=sts):
            result = svc.list_clusters(stdate=date.today())

        raions = [c["RAION"] for c in result]
        assert raions[-1] == "(без района)", f"Expected «без района» last, got {raions}"
        named = raions[:-1]
        assert named == sorted(named), f"Named raions should be alphabetical, got {named}"
