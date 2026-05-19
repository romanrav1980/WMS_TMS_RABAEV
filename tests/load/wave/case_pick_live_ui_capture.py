from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import tempfile
from urllib.parse import quote
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
RAW_UI_DIR = ROOT_DIR / "wiki-raw" / "wms_admin_ui_reference"
DEFAULT_REPORT = ROOT_DIR / "runtime" / "test-evidence" / "case-pick-wave-load" / "report.json"
DEFAULT_OUT_DIR = ROOT_DIR / "runtime" / "test-evidence" / "case-pick-wave-load" / "live-ui"


def main() -> None:
    args = parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)

    browser = find_browser()
    if not browser:
        raise RuntimeError("Headless Edge/Chrome was not found.")

    auth_page = write_auth_redirect_page(args.front_base, args.api_base, args.username, args.password)
    try:
        screenshots = []
        targets = build_targets(args.front_base, report)
        with tempfile.TemporaryDirectory(prefix="wms-live-ui-") as profile_dir:
            for target in targets:
                screenshots.append(capture_target(browser, profile_dir, auth_page, target, args.out_dir))
        evidence = {
            "run_prefix": report.get("run_prefix"),
            "pick_wave_id": report.get("pick_wave_id"),
            "source_report": str(args.report),
            "front_base": args.front_base,
            "api_base": args.api_base,
            "screenshots": screenshots,
        }
        evidence_path = args.out_dir / "live-ui-report.json"
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        write_live_ui_markdown(args.out_dir, evidence)
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
    finally:
        try:
            auth_page.unlink()
        except FileNotFoundError:
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture live raw ARM/TSD UI screenshots for a case-pick load report.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--front-base", default="http://127.0.0.1:3000")
    parser.add_argument("--api-base", default="http://127.0.0.1:8088")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    return parser.parse_args()


def build_targets(front_base: str, report: dict[str, Any]) -> list[dict[str, str]]:
    wave_id = report.get("pick_wave_id") or ""
    return [
        {
            "name": "arm-case-pick-management",
            "title": "ARM управления комплектацией",
            "url": f"{front_base}/case-pick-management.html?evidence=1&wave_id={wave_id}",
            "width": "1920",
            "height": "1080",
        },
        {
            "name": "tsd-case-pick",
            "title": "ТСД комплектовщика",
            "url": f"{front_base}/case-pick-tsd.html?evidence=1&scope=all&wave_id={wave_id}",
            "width": "486",
            "height": "936",
        },
    ]


def write_auth_redirect_page(front_base: str, api_base: str, username: str, password: str) -> Path:
    basic = base64.b64encode(f"{username}:{password}".encode("ascii")).decode("ascii")
    path = RAW_UI_DIR / "_evidence-auth-redirect.html"
    path.write_text(
        f"""<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>Evidence auth redirect</title></head>
<body>
<script>
const params = new URLSearchParams(window.location.search);
const target = params.get("target") || "{front_base}/case-pick-management.html";
sessionStorage.setItem("wmsAdminApiBase", "{api_base}");
sessionStorage.setItem("wmsAdminAuth", JSON.stringify({{
  apiBase: "{api_base}",
  basic: "Basic {basic}"
}}));
sessionStorage.setItem("wms.casepick.tsd.session", JSON.stringify({{
  session_id: "evidence",
  resource_id: "",
  operator_user_id: "evidence-picker",
  resource_code: "EVIDENCE-PICKER"
}}));
window.location.replace(target);
</script>
</body>
</html>
""",
        encoding="utf-8",
    )
    return path


def capture_target(browser: str, profile_dir: str, auth_page: Path, target: dict[str, str], out_dir: Path) -> dict[str, str]:
    output = (out_dir / f"{target['name']}.png").resolve()
    auth_url = f"http://127.0.0.1:3000/{auth_page.name}?target={quote(target['url'], safe='')}"
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--disable-gpu-compositing",
        "--disable-software-rasterizer",
        "--hide-scrollbars",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",
        f"--user-data-dir={profile_dir}",
        f"--window-size={target['width']},{target['height']}",
        f"--screenshot={output}",
        auth_url,
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return {
        "name": target["name"],
        "title": target["title"],
        "url": target["url"],
        "path": str(output),
        "returncode": str(completed.returncode),
        "exists": str(output.exists()),
        "bytes": str(output.stat().st_size if output.exists() else 0),
        "stderr_tail": completed.stderr[-500:],
    }


def write_live_ui_markdown(out_dir: Path, evidence: dict[str, Any]) -> None:
    rows = "\n".join(
        f"| {item['title']} | `{Path(item['path']).name}` | {item['exists']} | {item['bytes']} |"
        for item in evidence["screenshots"]
    )
    (out_dir / "live-ui-report.md").write_text(
        f"""# Case-pick live UI evidence

Run: `{evidence['run_prefix']}`

Wave ID: `{evidence['pick_wave_id']}`

| Screen | File | Exists | Bytes |
|---|---|---:|---:|
{rows}
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


if __name__ == "__main__":
    main()
