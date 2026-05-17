from __future__ import annotations

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import Settings, get_settings
from ..oracle_gateway import OracleGateway


SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}
HOP_BY_HOP_HEADERS = {
    "connection",
    "content-length",
    "host",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


class ApiAuditService:
    def __init__(
        self,
        gateway: OracleGateway | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.gateway = gateway or OracleGateway()
        self.settings = settings or get_settings()
        self.local_dir = Path(self.settings.audit_local_dir)
        if not self.local_dir.is_absolute():
            self.local_dir = Path.cwd() / self.local_dir

    def start_call(self, entry: dict[str, Any]) -> int | None:
        try:
            return self.gateway.call_number_plsql(
                """
                begin
                  :result := RRL_API_AUDIT_API.start_call(
                    p_request_id => :request_id,
                    p_replay_of_call_id => :replay_of_call_id,
                    p_replay_run_id => :replay_run_id,
                    p_method => :method,
                    p_path => :path,
                    p_query_string => :query_string,
                    p_url => :url,
                    p_client_ip => :client_ip,
                    p_user_agent => :user_agent,
                    p_request_headers_json => :request_headers_json,
                    p_request_body => :request_body,
                    p_request_body_sha256 => :request_body_sha256,
                    p_request_body_truncated => :request_body_truncated,
                    p_replayable => :replayable,
                    p_local_log_path => :local_log_path
                  );
                end;
                """,
                entry,
            )
        except Exception:
            return None

    def finish_call(self, api_call_id: int | None, entry: dict[str, Any]) -> None:
        if api_call_id is None:
            return
        try:
            self.gateway.execute_plsql(
                """
                begin
                  RRL_API_AUDIT_API.finish_call(
                    p_api_call_id => :api_call_id,
                    p_response_status => :response_status,
                    p_response_headers_json => :response_headers_json,
                    p_response_body => :response_body,
                    p_response_body_truncated => :response_body_truncated,
                    p_error_text => :error_text,
                    p_status => :status,
                    p_duration_ms => :duration_ms,
                    p_local_log_path => :local_log_path
                  );
                end;
                """,
                {"api_call_id": api_call_id, **entry},
            )
        except Exception:
            return

    def append_local(self, record: dict[str, Any]) -> str:
        self.local_dir.mkdir(parents=True, exist_ok=True)
        path = self.local_dir / f"{datetime.now(timezone.utc):%Y-%m-%d}.jsonl"
        payload = {**record, "logged_at": utc_now_iso()}
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, default=str))
            handle.write("\n")
        return str(path)

    def list_calls(
        self,
        from_call_id: int | None = None,
        to_call_id: int | None = None,
        from_at: str | None = None,
        to_at: str | None = None,
        method: str | None = None,
        path_like: str | None = None,
        status: str | None = None,
        replayable: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        where, params = self._build_call_filters(
            from_call_id=from_call_id,
            to_call_id=to_call_id,
            from_at=from_at,
            to_at=to_at,
            method=method,
            path_like=path_like,
            status=status,
            replayable=replayable,
        )
        params["limit"] = max(1, min(limit, 500))
        params["offset"] = max(0, offset)
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select q.*, rownum rn
                  from (
                    select API_CALL_ID, REQUEST_ID, REPLAY_OF_CALL_ID, REPLAY_RUN_ID,
                           METHOD, PATH, QUERY_STRING, CLIENT_IP, USER_AGENT,
                           RESPONSE_STATUS, STATUS, REPLAYABLE, REPLAY_COUNT,
                           LAST_REPLAY_AT, LAST_REPLAY_CALL_ID, LAST_REPLAY_ERROR, STARTED_AT,
                           FINISHED_AT, DURATION_MS, ERROR_TEXT, LOCAL_LOG_PATH
                      from RRL_API_CALL_LOG
                     {where}
                     order by API_CALL_ID desc
                  ) q
                 where rownum <= :offset + :limit
              )
             where rn > :offset
            """,
            params,
        )

    def get_call(self, api_call_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select API_CALL_ID, REQUEST_ID, REPLAY_OF_CALL_ID, REPLAY_RUN_ID,
                   METHOD, PATH, QUERY_STRING, URL, CLIENT_IP, USER_AGENT,
                   REQUEST_HEADERS_JSON, REQUEST_BODY, REQUEST_BODY_SHA256,
                   REQUEST_BODY_TRUNCATED, RESPONSE_STATUS, RESPONSE_HEADERS_JSON,
                   RESPONSE_BODY, RESPONSE_BODY_TRUNCATED, ERROR_TEXT, STATUS,
                   REPLAYABLE, REPLAY_COUNT, LAST_REPLAY_AT, LAST_REPLAY_CALL_ID,
                   LAST_REPLAY_ERROR, LOCAL_LOG_PATH, STARTED_AT, FINISHED_AT, DURATION_MS
              from RRL_API_CALL_LOG
             where API_CALL_ID = :api_call_id
            """,
            {"api_call_id": api_call_id},
        )
        return rows[0] if rows else {}

    def replay_calls(self, request: dict[str, Any]) -> dict[str, Any]:
        dry_run = bool(request.get("dry_run", True))
        continue_on_error = bool(request.get("continue_on_error", True))
        max_calls = max(1, min(int(request.get("max_calls") or 100), 500))
        replay_run_id = str(uuid.uuid4())
        call_ids = request.get("call_ids") or []

        if call_ids:
            params = {f"id{i}": int(call_id) for i, call_id in enumerate(call_ids[:max_calls])}
            placeholders = ", ".join(f":id{i}" for i in range(len(params)))
            rows = self.gateway.fetch_all(
                f"""
                select API_CALL_ID, REQUEST_ID, METHOD, PATH, QUERY_STRING,
                       REQUEST_HEADERS_JSON, REQUEST_BODY, REPLAYABLE, STATUS
                  from RRL_API_CALL_LOG
                 where API_CALL_ID in ({placeholders})
                   and REPLAYABLE = 1
                 order by API_CALL_ID
                """,
                params,
            )
        else:
            where, params = self._build_call_filters(
                from_call_id=request.get("from_call_id"),
                to_call_id=request.get("to_call_id"),
                from_at=request.get("from_at"),
                to_at=request.get("to_at"),
                method=request.get("method"),
                path_like=request.get("path_like"),
                status=request.get("status"),
                replayable=1,
            )
            params["max_calls"] = max_calls
            rows = self.gateway.fetch_all(
                f"""
                select *
                  from (
                    select API_CALL_ID, REQUEST_ID, METHOD, PATH, QUERY_STRING,
                           REQUEST_HEADERS_JSON, REQUEST_BODY, REPLAYABLE, STATUS
                      from RRL_API_CALL_LOG
                     {where}
                       {"and" if where else "where"} REPLAYABLE = 1
                     order by API_CALL_ID
                  )
                 where rownum <= :max_calls
                """,
                params,
            )

        results: list[dict[str, Any]] = []
        if dry_run:
            return {
                "dry_run": True,
                "replay_run_id": replay_run_id,
                "selected_count": len(rows),
                "calls": [
                    {
                        "api_call_id": row["api_call_id"],
                        "method": row["method"],
                        "path": row["path"],
                        "query_string": row["query_string"],
                        "status": row["status"],
                    }
                    for row in rows
                ],
            }

        for row in rows:
            started = time.perf_counter()
            try:
                replay_result = self._replay_one(row, replay_run_id)
                replay_result["duration_ms"] = int((time.perf_counter() - started) * 1000)
                results.append(replay_result)
                self._mark_replay(row["api_call_id"], replay_result.get("replay_call_id"), None)
            except Exception as exc:
                error_result = {
                    "api_call_id": row["api_call_id"],
                    "status": "ERROR",
                    "error": str(exc),
                    "duration_ms": int((time.perf_counter() - started) * 1000),
                }
                results.append(error_result)
                self._mark_replay(row["api_call_id"], None, str(exc))
                if not continue_on_error:
                    break

        return {
            "dry_run": False,
            "replay_run_id": replay_run_id,
            "selected_count": len(rows),
            "executed_count": len(results),
            "results": results,
        }

    def _replay_one(self, row: dict[str, Any], replay_run_id: str) -> dict[str, Any]:
        method = row["method"]
        query = row.get("query_string") or ""
        url = self.settings.audit_replay_base_url.rstrip("/") + row["path"]
        if query:
            url = f"{url}?{query}"

        headers = json_loads(row.get("request_headers_json")) or {}
        headers = {
            key: value
            for key, value in headers.items()
            if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() not in SENSITIVE_HEADERS
        }
        headers["X-WMS-Replay-Of"] = str(row["api_call_id"])
        headers["X-WMS-Replay-Run-Id"] = replay_run_id

        body = row.get("request_body")
        data = body.encode("utf-8") if body is not None and method not in {"GET", "HEAD"} else None

        req = Request(url=url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=60) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                replay_call_id = response.headers.get("X-WMS-API-Call-Id")
                return {
                    "api_call_id": row["api_call_id"],
                    "status": "DONE",
                    "response_status": response.status,
                    "replay_call_id": int(replay_call_id) if replay_call_id else None,
                    "response_preview": response_body[:500],
                }
        except HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            replay_call_id = exc.headers.get("X-WMS-API-Call-Id") if exc.headers else None
            return {
                "api_call_id": row["api_call_id"],
                "status": "HTTP_ERROR",
                "response_status": exc.code,
                "replay_call_id": int(replay_call_id) if replay_call_id else None,
                "response_preview": response_body[:500],
            }
        except URLError as exc:
            raise RuntimeError(f"Replay request failed: {exc}") from exc

    def _mark_replay(
        self, source_call_id: int, replay_call_id: int | None, error_text: str | None
    ) -> None:
        try:
            self.gateway.execute_plsql(
                """
                begin
                  RRL_API_AUDIT_API.mark_replay_result(
                    p_source_call_id => :source_call_id,
                    p_replay_call_id => :replay_call_id,
                    p_error_text => :error_text
                  );
                end;
                """,
                {
                    "source_call_id": source_call_id,
                    "replay_call_id": replay_call_id,
                    "error_text": error_text,
                },
            )
        except Exception:
            return

    def _build_call_filters(
        self,
        from_call_id: int | None = None,
        to_call_id: int | None = None,
        from_at: str | None = None,
        to_at: str | None = None,
        method: str | None = None,
        path_like: str | None = None,
        status: str | None = None,
        replayable: int | None = None,
    ) -> tuple[str, dict[str, Any]]:
        conditions: list[str] = ["not (PATH like '/api/admin/api-calls%' and STATUS = 'STARTED')"]
        params: dict[str, Any] = {}
        if from_call_id is not None:
            conditions.append("API_CALL_ID >= :from_call_id")
            params["from_call_id"] = from_call_id
        if to_call_id is not None:
            conditions.append("API_CALL_ID <= :to_call_id")
            params["to_call_id"] = to_call_id
        if from_at:
            conditions.append("STARTED_AT >= to_date(:from_at, 'YYYY-MM-DD HH24:MI:SS')")
            params["from_at"] = normalize_date_filter(from_at)
        if to_at:
            conditions.append("STARTED_AT <= to_date(:to_at, 'YYYY-MM-DD HH24:MI:SS')")
            params["to_at"] = normalize_date_filter(to_at)
        if method:
            conditions.append("METHOD = :method")
            params["method"] = method.upper()
        if path_like:
            conditions.append("lower(PATH) like lower(:path_like)")
            params["path_like"] = f"%{path_like}%"
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status
        if replayable is not None:
            conditions.append("REPLAYABLE = :replayable")
            params["replayable"] = replayable
        return (" where " + " and ".join(conditions) if conditions else ""), params


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


def json_loads(value: str | None) -> dict[str, str] | None:
    if not value:
        return None
    try:
        loaded = json.loads(value)
    except json.JSONDecodeError:
        return None
    return loaded if isinstance(loaded, dict) else None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def body_digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def decode_limited(body: bytes, max_chars: int) -> tuple[str, int]:
    text = body.decode("utf-8", errors="replace")
    if len(text) <= max_chars:
        return text, 0
    return text[:max_chars], 1


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        redacted[key] = "***" if key.lower() in SENSITIVE_HEADERS else value
    return redacted


def normalize_date_filter(value: str) -> str:
    value = value.strip().replace("T", " ")
    if len(value) == 10:
        return f"{value} 00:00:00"
    if len(value) == 16:
        return f"{value}:00"
    return value[:19]
