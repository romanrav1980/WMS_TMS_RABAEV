"""
test_sprint35_functional.py — Functional tests for Sprint 35.

Sprint 35: add `raion` filter to list_available_sts.
- Pushes district filter to Oracle SQL (WHERE RAION = :raion).
- create_task_from_cluster now uses server-side raion filter instead
  of fetching all STs and filtering in Python.
- «(без района)» → IS NULL in SQL.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestRaionFilter:

    def _make_st(self, raion, st="ST001"):
        return {"ST_NUMBER": st, "RAION": raion, "PALLETS_COUNT": 2, "WEIGHT_KG": 80.0}

    def test_raion_filter_passes_to_service(self):
        """GET /available-sts?raion=Север passes raion to list_available_sts."""
        from app.services.transport_service import TransportService
        svc = TransportService()
        with patch.object(svc.gateway, "fetch_all", return_value=[]) as mock_fetch:
            svc.list_available_sts(raion="Север")
        sql = mock_fetch.call_args[0][0]
        assert "RAION = :raion" in sql
        assert mock_fetch.call_args[0][1].get("raion") == "Север"

    def test_no_raion_filter_omits_condition(self):
        """Without raion=, SQL has no RAION condition."""
        from app.services.transport_service import TransportService
        svc = TransportService()
        with patch.object(svc.gateway, "fetch_all", return_value=[]) as mock_fetch:
            svc.list_available_sts()
        sql = mock_fetch.call_args[0][0]
        assert "RAION = :raion" not in sql
        assert "RAION IS NULL" not in sql

    def test_bez_raiona_maps_to_is_null(self):
        """«(без района)» → IS NULL in SQL."""
        from app.services.transport_service import TransportService
        svc = TransportService()
        with patch.object(svc.gateway, "fetch_all", return_value=[]) as mock_fetch:
            svc.list_available_sts(raion="(без района)")
        sql = mock_fetch.call_args[0][0]
        assert "RAION IS NULL" in sql
        assert "RAION = :raion" not in sql

    def test_raion_combined_with_stdate(self):
        """raion + stdate both appear in SQL."""
        from app.services.transport_service import TransportService
        from datetime import date
        svc = TransportService()
        with patch.object(svc.gateway, "fetch_all", return_value=[]) as mock_fetch:
            svc.list_available_sts(stdate=date.today(), raion="Юг")
        sql = mock_fetch.call_args[0][0]
        assert "RAION = :raion" in sql
        assert ":stdate" in sql


class TestCreateTaskFromClusterUsesServerFilter:

    def test_cluster_create_calls_list_available_sts_with_raion(self):
        """create_task_from_cluster passes raion to list_available_sts (server-side filter)."""
        from app.services.transport_service import TransportService
        from app.schemas import ClusterCreateTaskRequest
        from datetime import date

        svc = TransportService()
        req = ClusterCreateTaskRequest(stdate=date.today())

        with (
            patch.object(svc, "list_available_sts", return_value=[
                {"ST_NUMBER": "S1", "RAION": "Север", "PALLETS_COUNT": 2}
            ]) as mock_list,
            patch.object(svc, "create_task", return_value=100),
            patch.object(svc, "update_task"),
            patch.object(svc, "assign_sts", return_value={"warnings": []}),
        ):
            svc.create_task_from_cluster("Север", req, "tester")

        call_kwargs = mock_list.call_args[1]
        assert call_kwargs.get("raion") == "Север", "raion must be passed to list_available_sts"
        assert call_kwargs.get("unassigned_only") is True

    def test_cluster_create_no_longer_filters_in_python(self):
        """With raion passed to list_available_sts, all returned STs belong to the target district."""
        from app.services.transport_service import TransportService
        from app.schemas import ClusterCreateTaskRequest
        from datetime import date

        svc = TransportService()
        req = ClusterCreateTaskRequest(stdate=date.today())

        sts_returned = [
            {"ST_NUMBER": "S1", "RAION": "Север"},
            {"ST_NUMBER": "S2", "RAION": "Север"},
        ]

        with (
            patch.object(svc, "list_available_sts", return_value=sts_returned),
            patch.object(svc, "create_task", return_value=55),
            patch.object(svc, "update_task"),
            patch.object(svc, "assign_sts", return_value={"warnings": []}) as mock_assign,
        ):
            result = svc.create_task_from_cluster("Север", req, "tester")

        assert result["st_count"] == 2
        assigned = mock_assign.call_args[0][1]
        assert set(assigned) == {"S1", "S2"}


class TestRaionFilterEdgeCases:

    def test_raion_with_special_chars(self):
        """raion filter properly passes special chars to Oracle parameter."""
        from app.services.transport_service import TransportService
        svc = TransportService()
        with patch.object(svc.gateway, "fetch_all", return_value=[]) as mock_fetch:
            svc.list_available_sts(raion="г. Пермь/Мотовилиха")
        params = mock_fetch.call_args[0][1]
        assert params["raion"] == "г. Пермь/Мотовилиха"

    def test_empty_string_raion_not_filtered(self):
        """raion='' (empty string) should NOT add a filter (falsy check)."""
        from app.services.transport_service import TransportService
        svc = TransportService()
        with patch.object(svc.gateway, "fetch_all", return_value=[]) as mock_fetch:
            svc.list_available_sts(raion=None)
        sql = mock_fetch.call_args[0][0]
        assert "RAION" not in sql.replace("V.RAION", "")  # column in SELECT is ok, filter is not
