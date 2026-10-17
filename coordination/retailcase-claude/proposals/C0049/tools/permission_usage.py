# C-0049: обратный индекс «право → маршруты» из research/api_inventory.json + наличие права в живом снимке RIGHTS.
import json, re, sys
from pathlib import Path
inv = json.load(open("research/api_inventory.json", encoding="utf-8"))
snap = Path("C:/projects/TMS/reports/retailcase/2026-10-13/claude/C0049/live_rights_snapshot.txt").read_text(encoding="utf-8")
live = dict(re.findall(r"([a-z0-9_]+)\((\d+)\)", snap.split("ВСЕ ПРАВА")[1]))
idx = {}
for r in inv["routes"]:
    for p in r["permissions"]:
        idx.setdefault(p, []).append(f'{r["method"]} {r["path"]}')
md = ["# Права: где проверяются и есть ли в RIGHTS", "", f"Маршрутов: {len(inv['routes'])}; различных прав в API: {len(idx)}; в живом RIGHTS: {len(live)}.", "",
      "| Право | Групп в RIGHTS | Маршрутов | Чтение/изменение | Примеры |", "|---|---|---|---|---|"]
for p in sorted(set(idx) | set(live)):
    routes = idx.get(p, [])
    kinds = ("R" if any(x.startswith("GET") for x in routes) else "") + ("W" if any(not x.startswith("GET") for x in routes) else "")
    md.append(f"| `{p}` | {live.get(p, '—')} | {len(routes)} | {kinds or ('legacy/БД' if p in live else '—')} | {'; '.join(routes[:3])} |")
Path("research/permission_usage.md").write_text("\n".join(md), encoding="utf-8")
print(len(idx), "api perms;", len(set(live) - set(idx)), "live-only (legacy desktop/БД)")
print("in API not in any live group:", sorted(set(idx) - set(live)))
