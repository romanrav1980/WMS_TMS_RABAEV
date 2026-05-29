"""
screenshot.py — утилита скриншотов фронтенда TMS-2.

Используется агентом после успешного прохождения группы тестов.
Требует: pip install playwright && python -m playwright install chromium

Использование:
  python screenshot.py --page dispatcher --out reports/screenshots/01_dispatcher.png
  python screenshot.py --page planner    --out reports/screenshots/03_planner.png
  python screenshot.py --page gantt      --out reports/screenshots/06_gantt.png
  python screenshot.py --page billing    --out reports/screenshots/04_billing.png
  python screenshot.py --page fleet      --out reports/screenshots/05_fleet.png

Env vars:
  TMS_FRONTEND_URL  — по умолчанию http://localhost:3000
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

FRONTEND_URL = os.environ.get("TMS_FRONTEND_URL", "http://localhost:3000").rstrip("/")

PAGES: dict[str, str] = {
    "dispatcher": f"{FRONTEND_URL}/?page=transport",
    "routes":     f"{FRONTEND_URL}/?page=transport",
    "planner":    f"{FRONTEND_URL}/?page=planner",
    "gantt":      f"{FRONTEND_URL}/?page=gantt",
    "billing":    f"{FRONTEND_URL}/?page=transport",   # billing внутри диспетчера
    "fleet":      f"{FRONTEND_URL}/?page=fleet",
    "kpi":        f"{FRONTEND_URL}/?page=kpi",
    "users":      f"{FRONTEND_URL}/?page=users",
}

# CSS-селекторы: ждём появления ключевого элемента страницы
WAIT_SELECTORS: dict[str, str] = {
    "dispatcher": ".dispatch-trips-table-wrap, .dispatch-avail-table, table",
    "routes":     ".dispatch-trips-table-wrap, table",
    "planner":    ".leaflet-container, canvas",
    "gantt":      "svg, .gantt-svg",
    "billing":    ".dispatch-trips-table-wrap, table",
    "fleet":      "table",
    "kpi":        "canvas, .kpi-dashboard, table",
    "users":      "table",
}


def take_screenshot(
    page_name: str,
    output_path: str,
    width: int = 1600,
    height: int = 900,
    wait_extra_ms: int = 2000,
) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright не установлен. Запустите: pip install playwright && python -m playwright install chromium")
        sys.exit(1)

    url = PAGES.get(page_name, FRONTEND_URL)
    selector = WAIT_SELECTORS.get(page_name, "body")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": width, "height": height},
            locale="ru-RU",
        )
        page = context.new_page()

        print(f"Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=30_000)

        # Ждём появления ключевого элемента
        try:
            page.wait_for_selector(selector, timeout=15_000, state="visible")
            print(f"Element found: {selector}")
        except Exception as exc:
            print(f"WARN: selector not found ({exc}), taking screenshot anyway")

        # Дополнительное ожидание для рендера данных (таблицы, карты)
        page.wait_for_timeout(wait_extra_ms)

        page.screenshot(path=output_path, full_page=False)
        print(f"Screenshot saved: {output_path}")

        context.close()
        browser.close()


def _batch_all(out_dir: str) -> None:
    """Сделать скриншоты всех страниц сразу."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for page_name in PAGES:
        out = f"{out_dir}/{page_name}.png"
        take_screenshot(page_name, out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TMS-2 frontend screenshot utility")
    parser.add_argument(
        "--page",
        choices=list(PAGES.keys()) + ["all"],
        required=True,
        help="Страница для скриншота. 'all' — все страницы сразу.",
    )
    parser.add_argument("--out", default=None, help="Путь к файлу PNG")
    parser.add_argument("--outdir", default="reports/screenshots", help="Папка для --page all")
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--wait", type=int, default=2000, help="Доп. ожидание (ms) после загрузки")
    args = parser.parse_args()

    if args.page == "all":
        _batch_all(args.outdir)
    else:
        if not args.out:
            args.out = f"{args.outdir}/{args.page}.png"
        take_screenshot(args.page, args.out, args.width, args.height, args.wait)
