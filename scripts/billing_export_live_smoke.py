"""Read-only HTTP workbook acceptance across the real audit middleware."""
import io
import json
import os
from pathlib import Path
from time import perf_counter
import zipfile
import httpx
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8088/api/admin/transport"


def workbook(client, path):
    started = perf_counter()
    response = client.get(path)
    assert response.status_code == 200, (path, response.status_code, response.text[:100])
    assert response.headers["content-type"].split(";")[0] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert int(response.headers["content-length"]) == len(response.content)
    assert response.headers["content-disposition"].startswith("attachment;")
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert archive.testzip() is None
        assert {"[Content_Types].xml", "xl/workbook.xml", "xl/worksheets/sheet1.xml"} <= set(archive.namelist())
        ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ["".join(node.itertext()) for node in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        rows = []
        for line in ET.fromstring(archive.read("xl/worksheets/sheet1.xml")).findall("x:sheetData/x:row", ns):
            values = [None] * 9
            for cell in line:
                column = 0
                for letter in cell.attrib["r"].rstrip("0123456789"):
                    column = column * 26 + ord(letter) - ord("A") + 1
                value = cell.find("x:v", ns)
                text = value.text if value is not None else None
                if cell.attrib.get("t") == "s":
                    text = strings[int(text)]
                elif cell.attrib.get("t") == "inlineStr":
                    inline = cell.find("x:is", ns)
                    text = "".join(inline.itertext()) if inline is not None else ""
                elif text is not None:
                    text = float(text)
                values[column - 1] = text
            while len(rows) < int(line.attrib["r"]) - 1:
                rows.append([None] * 9)
            rows.append(values)
    return rows, dict(path=path, bytes=len(response.content), crc="PASS", content_length="EXACT",
        elapsed_ms=round((perf_counter() - started) * 1000, 2))


def main():
    records = []
    auth = (os.environ.get("TMS_EXPORT_SMOKE_USER", "admin"), os.environ.get("TMS_EXPORT_SMOKE_PASSWORD", "admin123"))
    with httpx.Client(base_url=BASE, auth=auth, timeout=60) as client:
        orders = client.get("/billing/orders").json()
        assert orders and len(orders) <= 2000
        rows, result = workbook(client, "/billing/orders/export.xlsx")
        assert len(rows[4:-1]) == len(orders)
        assert abs(float(rows[-1][5]) - sum(float(row["total_price"]) for row in orders)) < 0.005
        records.append({**result, "rows": len(orders), "totals": "MATCH_LIVE_REGISTRY"})
        order_id = next(row["order_id"] for row in orders if row["task_count"] > 0)
        tasks_response = client.get(f"/billing/orders/{order_id}/tasks")
        assert tasks_response.status_code == 200
        tasks = tasks_response.json()
        rows, result = workbook(client, f"/billing/orders/{order_id}/export.xlsx")
        assert [int(row[0]) for row in rows[8:-1]] == [row["tt_id"] for row in tasks]
        assert abs(float(rows[-1][4]) - sum(float(row["price"]) for row in tasks)) < 0.005
        records.append({**result, "rows": len(tasks), "totals": "MATCH_LIVE_TASKS"})
        rows, result = workbook(client, "/billing/orders/export.xlsx?company=NO_MATCH_EXPORT_20261015_8cbe567")
        assert len(rows) == 5 and float(rows[-1][5]) == 0
        records.append({**result, "rows": 0, "empty_workbook": "VALID"})
        assert client.get("/billing/orders/-999999/export.xlsx").status_code == 404
    with httpx.Client(base_url=BASE, timeout=30) as client:
        assert client.get("/billing/orders/export.xlsx").status_code == 401
        assert client.get("/billing/orders/528/export.xlsx").status_code == 401
    report = dict(status="PASS", business_data="READ_ONLY", stock_effect="NONE", workbooks=records,
        checks=["registry_crc_rows_and_totals", "order_crc_tasks_and_totals", "empty_valid_xlsx", "missing_order_404", "unauthenticated_401"])
    path = ROOT / "reports/retailcase/2026-10-15/dispatch-scope/billing-exports.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
