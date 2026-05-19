from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import wave_replenishment_load_test as load


ROOT_DIR = Path(__file__).resolve().parents[3]
RAW_UI_DIR = ROOT_DIR / "wiki-raw" / "wms_admin_ui_reference"
DEFAULT_OUT_DIR = ROOT_DIR / "runtime" / "test-evidence" / "wave-10sku-stock" / "stage-evidence"


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    run_prefix = f"{load.LOAD_PREFIX}-{load.random_suffix(6)}"
    state = load.LoadState(run_prefix=run_prefix)
    client = load.ApiClient(args.base_url, args.username, args.password, state)

    load.wait_for_api(client)
    load.cleanup_load_data()
    fixture = load.create_fixture(run_prefix, 10, "IMMEDIATE", False, 9)
    stages: list[dict[str, Any]] = []
    started = time.perf_counter()
    snapshot(stages, "T0_FIXTURE", "Создано чистое модельное состояние склада", run_prefix, None)

    wave = client.post(
        "/api/picking/waves",
        {
            "wave_code": f"{run_prefix}-W001",
            "wave_name": f"{run_prefix} evidence wave",
            "ware_id": fixture["ware_id"],
            "max_customers": 30,
            "created_by": run_prefix,
        },
        metric_endpoint="POST /api/picking/waves",
    )
    wave_id = int(wave["pick_wave_id"])
    for plan_id in fixture["pick_plan_ids"]:
        client.post(
            f"/api/picking/waves/{wave_id}/plans",
            {"pick_plan_id": plan_id, "created_by": run_prefix},
            metric_endpoint="POST /api/picking/waves/{id}/plans",
        )
    client.post(
        f"/api/picking/waves/{wave_id}/calculate",
        {"updated_by": run_prefix},
        metric_endpoint="POST /api/picking/waves/{id}/calculate",
    )
    snapshot(stages, "T1_CALCULATED", "Волна создана, планы добавлены, расчет выполнен", run_prefix, wave_id)

    client.post(
        f"/api/picking/waves/{wave_id}/launch",
        {"updated_by": run_prefix},
        metric_endpoint="POST /api/picking/waves/{id}/launch",
    )
    snapshot(stages, "T2_LAUNCHED", "Волна запущена: созданы hard reservations и первые задачи водителя", run_prefix, wave_id)

    live_screenshots = capture_live_ui(args, run_prefix, wave_id)
    executed_task_ids: set[int] = set()
    checkpoints = {1: "T3_FIRST_MOVE", 3: "T4_THREE_MOVES", 6: "T5_SIX_MOVES", 9: "T6_FINAL"}
    titles = {
        "T3_FIRST_MOVE": "Закрыта первая задача ричтрака",
        "T4_THREE_MOVES": "Закрыты три задачи ричтрака",
        "T5_SIX_MOVES": "Закрыты шесть задач ричтрака",
        "T6_FINAL": "Все пополнения закрыты, резервы consumed, физический остаток перемещен",
    }

    for _ in range(20):
        rows = client.get(
            f"/api/picking/waves/{wave_id}/replenishment-tasks?limit=500",
            metric_endpoint="GET /api/picking/waves/{id}/replenishment-tasks",
        )
        open_rows = [
            row
            for row in rows
            if row.get("warehouse_task_id")
            and row.get("warehouse_task_status") != "DONE"
            and int(row["warehouse_task_id"]) not in executed_task_ids
        ]
        if not open_rows:
            if all(row.get("status") in {"DONE", "CANCELLED"} for row in rows):
                break
            client.post(
                f"/api/picking/waves/{wave_id}/replenishment/minimax-check",
                {"updated_by": run_prefix},
                metric_endpoint="POST /api/picking/waves/{id}/replenishment/minimax-check",
            )
            continue
        for row in open_rows:
            load.execute_replenishment_task(client, run_prefix, row)
            executed_task_ids.add(int(row["warehouse_task_id"]))
            client.post(
                f"/api/picking/waves/{wave_id}/replenishment/minimax-check",
                {"updated_by": run_prefix},
                metric_endpoint="POST /api/picking/waves/{id}/replenishment/minimax-check",
            )
            code = checkpoints.get(len(executed_task_ids))
            if code:
                snapshot(stages, code, titles[code], run_prefix, wave_id)
        if len(executed_task_ids) >= 9:
            break

    diagnostics = load.collect_diagnostics(run_prefix)
    load.assert_diagnostics(diagnostics, expected_waves=1, dynamic_pick_faces=9, drain_replenishment_queue=True)
    report = {
        "run_prefix": run_prefix,
        "pick_wave_id": wave_id,
        "elapsed_s": round(time.perf_counter() - started, 3),
        "request_count": len(state.metrics),
        "failed_request_count": len([metric for metric in state.metrics if not metric.ok]),
        "diagnostics": diagnostics,
        "stages": stages,
        "live_screenshots": live_screenshots,
        "latency_ms": {
            endpoint: load.summarize([metric.elapsed_ms for metric in state.metrics if metric.endpoint == endpoint])
            for endpoint in sorted({metric.endpoint for metric in state.metrics})
        },
    }
    report_path = args.out_dir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    presentation = write_presentation(args.out_dir, report)
    report["screenshots"] = capture_stage_screenshots(args.out_dir, presentation, stages)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    write_markdown(args.out_dir, report)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create staged screenshots for wave replenishment stock evidence.")
    parser.add_argument("--base-url", default=load.DEFAULT_BASE_URL)
    parser.add_argument("--front-base", default="http://127.0.0.1:3000")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def snapshot(stages: list[dict[str, Any]], code: str, title: str, run_prefix: str, wave_id: int | None) -> None:
    stages.append(
        {
            "code": code,
            "title": title,
            "diagnostics": collect_stage_diagnostics(run_prefix, wave_id),
            "stocks": collect_stock_rows(run_prefix),
            "tasks": collect_task_rows(run_prefix),
        }
    )


def collect_stage_diagnostics(run_prefix: str, wave_id: int | None) -> dict[str, Any]:
    base = load.collect_diagnostics(run_prefix)
    with load.connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            select nvl(sum(case when r.CELL like :source_like then r.REMAIN else 0 end), 0) SOURCE_QTY,
                   nvl(sum(case when r.CELL not like :source_like then r.REMAIN else 0 end), 0) PICKFACE_QTY
              from RRL_REMAINS r
             where r.UID_POLETA like :pallet_like
            """,
            {"source_like": f"{run_prefix[-6:]}-S%", "pallet_like": f"{run_prefix}%"},
        )
        source_qty, pickface_qty = cursor.fetchone()
        cursor.execute(
            """
            select count(*), nvl(sum(QTY), 0)
              from RRL_WAREHOUSE_TASK_STOCK_MOVE
             where UID_PALLET like :pallet_like
            """,
            {"pallet_like": f"{run_prefix}%"},
        )
        move_rows, moved_qty = cursor.fetchone()
        readiness = {}
        if wave_id:
            try:
                # Keep the report useful even if readiness changes later.
                readiness = {}
            except Exception:
                readiness = {}
    base.update(
        {
            "source_qty": float(source_qty or 0),
            "pickface_qty": float(pickface_qty or 0),
            "stock_move_rows": int(move_rows or 0),
            "stock_moved_qty": float(moved_qty or 0),
            "readiness": readiness,
        }
    )
    return base


def collect_stock_rows(run_prefix: str) -> list[dict[str, Any]]:
    with load.connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            select CELL, count(*) PALLET_ROWS, nvl(sum(REMAIN), 0) QTY
              from RRL_REMAINS
             where UID_POLETA like :pallet_like
             group by CELL
             order by CELL
            """,
            {"pallet_like": f"{run_prefix}%"},
        )
        return [{"cell": row[0], "pallet_rows": int(row[1] or 0), "qty": float(row[2] or 0)} for row in cursor.fetchall()]


def collect_task_rows(run_prefix: str) -> list[dict[str, Any]]:
    with load.connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            select TASK_ID, STATUS, UID_PALLET, FROM_CELL, TO_CELL, QTY, FACT_QTY
              from RRL_WAREHOUSE_TASK
             where TASK_SOURCE = 'WAVE'
               and TASK_TYPE = 'REPLENISHMENT'
               and SOURCE_DOC_ID in (
                 select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
               )
             order by TASK_ID
            """,
            {"marker": run_prefix},
        )
        return [
            {
                "task_id": int(row[0]),
                "status": row[1],
                "uid_pallet": row[2],
                "from_cell": row[3],
                "to_cell": row[4],
                "qty": float(row[5] or 0),
                "fact_qty": float(row[6] or 0),
            }
            for row in cursor.fetchall()
        ]


def write_presentation(out_dir: Path, report: dict[str, Any]) -> Path:
    path = out_dir / "evidence-presentation.html"
    sections = "\n".join(render_stage(stage) for stage in report["stages"])
    path.write_text(
        f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Wave replenishment stock evidence</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f6f8fb; color: #10233f; }}
    .slide {{ width: 1366px; min-height: 768px; box-sizing: border-box; padding: 28px; border-bottom: 1px solid #dfe8f5; }}
    h1, h2 {{ margin: 0 0 12px; }}
    .meta {{ color: #52667f; font-weight: 700; margin-bottom: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin: 14px 0; }}
    .card {{ background: white; border: 1px solid #dfe8f5; border-radius: 8px; padding: 13px; }}
    .card b {{ display: block; color: #52667f; font-size: 12px; }}
    .card strong {{ display: block; margin-top: 4px; font-size: 26px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #dfe8f5; margin-top: 12px; }}
    th, td {{ padding: 8px 10px; border-bottom: 1px solid #edf2f7; text-align: left; font-size: 13px; }}
    .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    .ok {{ color: #07884f; font-weight: 800; }}
  </style>
</head>
<body>
  <section class="slide" id="summary">
    <h1>Evidence: пополнение ячеек отбора под волну</h1>
    <div class="meta">Run: {report["run_prefix"]} · Wave #{report["pick_wave_id"]} · elapsed {report["elapsed_s"]} sec</div>
    <div class="grid">
      {card("Планы", report["diagnostics"]["pick_plans"])}
      {card("Пополнения", report["diagnostics"]["wave_replenishment_tasks"])}
      {card("WHT DONE", report["diagnostics"]["done_warehouse_replenishment_tasks"])}
      {card("SYNCED", report["diagnostics"]["synced_warehouse_replenishment_sync_rows"])}
      {card("Moved qty", report["stages"][-1]["diagnostics"]["stock_moved_qty"])}
      {card("API errors", report["failed_request_count"])}
    </div>
    <table>
      <tr><th>Доказательство</th><th>Результат</th></tr>
      <tr><td>Hard source reservations</td><td>{report["diagnostics"]["source_reservations"]}, consumed {report["diagnostics"]["consumed_source_reservations"]}</td></tr>
      <tr><td>Physical stock bridge</td><td>{report["stages"][-1]["diagnostics"]["stock_move_rows"]} ledger rows, {report["stages"][-1]["diagnostics"]["stock_moved_qty"]} boxes moved</td></tr>
      <tr><td>Oracle objects</td><td class="ok">{report["diagnostics"]["invalid_objects"]} invalid</td></tr>
    </table>
  </section>
  {sections}
</body>
</html>
""",
        encoding="utf-8",
    )
    return path


def render_stage(stage: dict[str, Any]) -> str:
    d = stage["diagnostics"]
    stock_rows = "\n".join(
        f"<tr><td>{html(row['cell'])}</td><td>{row['pallet_rows']}</td><td>{row['qty']:g}</td></tr>"
        for row in stage["stocks"]
    )
    task_rows = "\n".join(
        f"<tr><td>{row['task_id']}</td><td>{html(row['status'])}</td><td>{html(row['from_cell'])}</td><td>{html(row['to_cell'])}</td><td>{row['qty']:g}</td><td>{row['fact_qty']:g}</td></tr>"
        for row in stage["tasks"][:12]
    )
    return f"""<section class="slide" id="{stage['code']}">
  <h2>{stage['code']}: {html(stage['title'])}</h2>
  <div class="grid">
    {card("Source qty", d["source_qty"])}
    {card("Pick-face qty", d["pickface_qty"])}
    {card("Move rows", d["stock_move_rows"])}
    {card("Moved qty", d["stock_moved_qty"])}
    {card("WHT DONE", d["done_warehouse_replenishment_tasks"])}
    {card("Reservations consumed", d["consumed_source_reservations"])}
  </div>
  <div class="cols">
    <div>
      <h2>Физические остатки</h2>
      <table><tr><th>Ячейка</th><th>Строк</th><th>Кол-во</th></tr>{stock_rows}</table>
    </div>
    <div>
      <h2>Задачи ричтрака</h2>
      <table><tr><th>ID</th><th>Статус</th><th>Откуда</th><th>Куда</th><th>План</th><th>Факт</th></tr>{task_rows}</table>
    </div>
  </div>
</section>"""


def card(title: str, value: Any) -> str:
    return f"<div class=\"card\"><b>{html(title)}</b><strong>{html(format_value(value))}</strong></div>"


def format_value(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def capture_stage_screenshots(out_dir: Path, presentation_path: Path, stages: list[dict[str, Any]]) -> list[dict[str, str]]:
    browser = find_browser()
    if not browser:
        return [{"status": "skipped", "reason": "headless browser not found"}]
    html_text = presentation_path.read_text(encoding="utf-8")
    html_prefix = html_text.split("<body>", 1)[0] + "<body>"
    results = []
    for code in ["summary"] + [stage["code"] for stage in stages]:
        capture_html = write_single_section(out_dir, html_text, html_prefix, code)
        output = (out_dir / f"{code}.png").resolve()
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            "--window-size=1366,768",
            f"--screenshot={output}",
            f"file:///{capture_html.resolve().as_posix()}",
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        results.append({"name": code, "path": str(output), "returncode": completed.returncode, "bytes": output.stat().st_size if output.exists() else 0})
    return results


def write_single_section(out_dir: Path, html_text: str, html_prefix: str, code: str) -> Path:
    marker = f'id="{code}"'
    marker_pos = html_text.find(marker)
    if marker_pos < 0:
        raise ValueError(f"Section {code} was not found.")
    section_start = html_text.rfind("<section", 0, marker_pos)
    section_end = html_text.find("</section>", marker_pos)
    section = html_text[section_start : section_end + len("</section>")]
    path = out_dir / f"_{code}.capture.html"
    path.write_text(f"{html_prefix}\n{section}\n</body>\n</html>\n", encoding="utf-8")
    return path


def capture_live_ui(args: argparse.Namespace, run_prefix: str, wave_id: int) -> list[dict[str, Any]]:
    browser = find_browser()
    if not browser:
        return [{"status": "skipped", "reason": "headless browser not found"}]
    auth_page = write_auth_redirect_page(args.front_base, args.base_url, args.username, args.password)
    targets = [
        {
            "name": "ARM-wave-replenishment-T2",
            "url": f"{args.front_base}/wave-replenishment.html?wave_id={wave_id}",
            "width": "1920",
            "height": "1080",
        },
        {
            "name": "TSD-reachtruck-T2",
            "url": f"{args.front_base}/reachtruck-tsd.html?task_source=WAVE&task_type=REPLENISHMENT&source_doc_id={wave_id}",
            "width": "486",
            "height": "936",
        },
    ]
    results = []
    try:
        with tempfile.TemporaryDirectory(prefix="wms-wave-evidence-") as profile_dir:
            for target in targets:
                output = (args.out_dir / f"{target['name']}.png").resolve()
                auth_url = f"{args.front_base}/{auth_page.name}?target={quote(target['url'], safe='')}&run_prefix={quote(run_prefix)}"
                cmd = [
                    browser,
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=15000",
                    f"--user-data-dir={profile_dir}",
                    f"--window-size={target['width']},{target['height']}",
                    f"--screenshot={output}",
                    auth_url,
                ]
                completed = subprocess.run(cmd, capture_output=True, text=True, timeout=70)
                results.append({"name": target["name"], "url": target["url"], "path": str(output), "returncode": completed.returncode, "bytes": output.stat().st_size if output.exists() else 0})
    finally:
        try:
            auth_page.unlink()
        except FileNotFoundError:
            pass
    return results


def write_auth_redirect_page(front_base: str, api_base: str, username: str, password: str) -> Path:
    basic = base64.b64encode(f"{username}:{password}".encode("ascii")).decode("ascii")
    path = RAW_UI_DIR / "_wave-evidence-auth-redirect.html"
    path.write_text(
        f"""<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>Evidence auth redirect</title></head>
<body>
<script>
const params = new URLSearchParams(window.location.search);
const target = params.get("target") || "{front_base}/wave-replenishment.html";
const runPrefix = params.get("run_prefix") || "evidence";
sessionStorage.setItem("wmsAdminApiBase", "{api_base}");
sessionStorage.setItem("wmsAdminAuth", JSON.stringify({{
  apiBase: "{api_base}",
  basic: "Basic {basic}"
}}));
sessionStorage.setItem("wms.reachtruck.tsd.session", JSON.stringify({{
  session_id: "evidence",
  resource_id: "",
  operator_user_id: runPrefix + "-DRIVER",
  resource_code: "EVIDENCE-REACHTRUCK"
}}));
window.location.replace(target);
</script>
</body>
</html>
""",
        encoding="utf-8",
    )
    return path


def write_markdown(out_dir: Path, report: dict[str, Any]) -> None:
    stage_rows = "\n".join(f"| {stage['code']} | {stage['title']} | {stage['diagnostics']['source_qty']:g} | {stage['diagnostics']['pickface_qty']:g} | {stage['diagnostics']['stock_moved_qty']:g} |" for stage in report["stages"])
    screenshot_rows = "\n".join(f"| {Path(item['path']).name} | {item.get('bytes', 0)} |" for item in report.get("screenshots", []) + report.get("live_screenshots", []) if item.get("path"))
    (out_dir / "report.md").write_text(
        f"""# Wave replenishment stage evidence

Run: `{report['run_prefix']}`

Wave ID: `{report['pick_wave_id']}`

Elapsed seconds: `{report['elapsed_s']}`

## Stage Evidence

| Stage | Title | Source qty | Pick-face qty | Moved qty |
|---|---|---:|---:|---:|
{stage_rows}

## Screenshots

| File | Bytes |
|---|---:|
{screenshot_rows}
""",
        encoding="utf-8",
    )


def find_browser() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    for command in ("msedge", "chrome", "chromium"):
        found = shutil.which(command)
        if found:
            return found
    return None


def html(value: Any) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    main()
