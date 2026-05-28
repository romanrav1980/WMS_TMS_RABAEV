"""
test_sprint29_functional.py — Functional tests for Sprint 29.

Sprint 29 adds POST /clusters/{raion}/create-task (Phase 2 semi-auto):
- Creates a transport task from all unassigned STs in a district cluster.
- Assigns vehicle/driver/dock if provided.
- Returns task_id, raion, st_count, warnings.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date


# ---------------------------------------------------------------------------
# Unit tests for TransportService.create_task_from_cluster
# ---------------------------------------------------------------------------

@pytest.fixture()
def svc():
    from api.wms_api_server.app.services.transport_service import TransportService
    return TransportService()


def _make_st(raion: str, st_number: str = "ST001") -> dict:
    return {
        "ST_NUMBER": st_number,
        "RAION": raion,
        "PALLETS": 2,
        "WEIGHT": 100.0,
    }


class TestCreateTaskFromCluster:

    def test_raises_404_when_no_sts_in_raion(self, svc):
        from fastapi import HTTPException
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest

        req = ClusterCreateTaskRequest(stdate=date.today())
        with patch.object(svc, "list_available_sts", return_value=[]) as mock_list:
            with pytest.raises(HTTPException) as exc:
                svc.create_task_from_cluster("ТестРайон", req, "tester")
        assert exc.value.status_code == 404
        assert "ТестРайон" in exc.value.detail
        assert mock_list.call_args.kwargs["raion"] == "ТестРайон"

    def test_creates_task_and_assigns_sts(self, svc):
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest

        req = ClusterCreateTaskRequest(stdate=date.today())
        sts = [_make_st("Север", f"ST{i:03d}") for i in range(3)]

        with (
            patch.object(svc, "list_available_sts", return_value=sts),
            patch.object(svc, "create_task", return_value=42) as mock_create,
            patch.object(svc, "update_task") as mock_update,
            patch.object(svc, "assign_sts", return_value={"warnings": []}) as mock_assign,
        ):
            result = svc.create_task_from_cluster("Север", req, "tester")

        assert result["task_id"] == 42
        assert result["raion"] == "Север"
        assert result["st_count"] == 3
        assert result["warnings"] == []
        mock_create.assert_called_once()
        mock_update.assert_not_called()  # no vehicle/driver/dock provided
        mock_assign.assert_called_once_with(42, ["ST000", "ST001", "ST002"], "tester")

    def test_calls_update_task_when_vehicle_provided(self, svc):
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest

        req = ClusterCreateTaskRequest(stdate=date.today(), vehicle="А001АА", dock="Д1")
        sts = [_make_st("Юг", "ST777")]

        with (
            patch.object(svc, "list_available_sts", return_value=sts),
            patch.object(svc, "create_task", return_value=99),
            patch.object(svc, "update_task") as mock_update,
            patch.object(svc, "assign_sts", return_value={"warnings": []}),
        ):
            result = svc.create_task_from_cluster("Юг", req, "tester")

        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][0] == 99
        update_req = call_args[0][1]
        assert update_req.transport == "А001АА"
        assert update_req.dock == "Д1"

    def test_raion_is_passed_to_available_sts_query(self, svc):
        """Cluster creation relies on server-side raion filtering in list_available_sts."""
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest
        from fastapi import HTTPException

        req = ClusterCreateTaskRequest(stdate=date.today())

        with patch.object(svc, "list_available_sts", return_value=[]) as mock_list:
            with pytest.raises(HTTPException) as exc:
                svc.create_task_from_cluster("Север", req, "tester")
        assert exc.value.status_code == 404
        assert mock_list.call_args.kwargs["raion"] == "Север"

    def test_sts_without_raion_appear_as_no_raion(self, svc):
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest

        req = ClusterCreateTaskRequest(stdate=date.today())
        no_raion_st = {"ST_NUMBER": "ST999", "RAION": None, "PALLETS": 1, "WEIGHT": 50.0}

        with (
            patch.object(svc, "list_available_sts", return_value=[no_raion_st]),
            patch.object(svc, "create_task", return_value=77),
            patch.object(svc, "update_task"),
            patch.object(svc, "assign_sts", return_value={"warnings": []}) as mock_assign,
        ):
            result = svc.create_task_from_cluster("(без района)", req, "tester")

        assert result["st_count"] == 1
        mock_assign.assert_called_once_with(77, ["ST999"], "tester")


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

class TestClusterCreateTaskRequestSchema:

    def test_default_transtype(self):
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest
        req = ClusterCreateTaskRequest(stdate=date.today())
        assert req.transtype == "10"

    def test_optional_fields_are_none_by_default(self):
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest
        req = ClusterCreateTaskRequest(stdate=date.today())
        assert req.vehicle is None
        assert req.driver_id is None
        assert req.dock is None
        assert req.ware_ids is None

    def test_all_fields_accepted(self):
        from api.wms_api_server.app.schemas import ClusterCreateTaskRequest
        req = ClusterCreateTaskRequest(
            stdate=date.today(),
            transtype="20",
            vehicle="Т368ХН",
            driver_id=5,
            dock="Д2",
            ware_ids=[1, 2, 3],
        )
        assert req.transtype == "20"
        assert req.vehicle == "Т368ХН"
        assert req.driver_id == 5
        assert req.dock == "Д2"
        assert req.ware_ids == [1, 2, 3]
