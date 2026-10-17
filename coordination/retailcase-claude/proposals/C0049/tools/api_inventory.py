# C-0049: инвентаризация FastAPI маршрутов (метод, путь, право) статическим разбором исходников — без запуска и без БД.
# Запуск: python tools/api_inventory.py research/api_inventory.json  (рядом пишется research/api_inventory.md)
import json, re, sys
from pathlib import Path

APP = Path("C:/projects/TMS/api/wms_api_server/app")
DEP = re.compile(r'Depends\(\s*([a-z_][a-z0-9_]*)\s*\)')

const = {}
for f in APP.rglob("*.py"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    for name, value in re.findall(r'^\s*([A-Z][A-Z0-9_]*PERMISSION[A-Z0-9_]*)\s*=\s*"([a-z0-9_]+)"', text, re.M):
        const.setdefault(name, value)


def resolve(token: str) -> str:
    token = token.strip()
    return token.strip('"') if token.startswith('"') else const.get(token, token)


# Права заглушек из main.py: app.dependency_overrides[module.dep] = require_permission(...)
overrides = {}
for n, x in re.findall(r'dependency_overrides\[[\w.]*?\.?([a-z_][a-z0-9_]*)\]\s*=\s*require_permission\(\s*([A-Z0-9_]+|"[a-z0-9_]+")', (APP / "main.py").read_text(encoding="utf-8")):
    overrides.setdefault(n, resolve(x))

rows = []
for f in sorted(APP.rglob("*.py")):
    s = f.read_text(encoding="utf-8", errors="ignore")
    if "@router." not in s:
        continue
    # Алиасы вида `x_view = require_permission(CONST)` и функции-зависимости с require_permission внутри.
    alias = {n: resolve(x) for n, x in re.findall(r'^\s*([a-z_][a-z0-9_]*)\s*=\s*require_permission\(\s*([A-Z0-9_]+|"[a-z0-9_]+")\s*\)', s, re.M)}
    for n, x in re.findall(r'^def ([a-z_][a-z0-9_]*)\([^)]*require_permission\(\s*([A-Z0-9_]+|"[a-z0-9_]+")', s, re.M | re.S):
        alias.setdefault(n, resolve(x))
    prefix_match = re.search(r'APIRouter\([^)]*prefix\s*=\s*"([^"]*)"', s)
    prefix = prefix_match[1] if prefix_match else ""
    for part in re.split(r'(?=^@router\.)', s, flags=re.M)[1:]:
        m = re.match(r'@router\.(get|post|put|patch|delete)\(\s*"([^"]*)"', part)
        if not m:
            continue
        body = part[:2500]
        perms = {resolve(x) for x in re.findall(r'require_permission\(\s*([A-Z0-9_]+|"[a-z0-9_]+")\s*\)', body)}
        deps = set(DEP.findall(body)) - {"get_current_admin", "get_settings"}
        perms |= {alias[d] for d in deps if d in alias} | {overrides[d] for d in deps if d in overrides}
        rows.append({"method": m[1].upper(), "path": prefix + m[2], "permissions": sorted(perms),
                     "deps": sorted(d for d in deps if d not in alias and d not in overrides),
                     "file": str(f.relative_to(APP.parent)).replace("\\", "/")})

json.dump({"constants": const, "routes": rows}, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)

md = [f"# Инвентаризация API (статический разбор, {len(rows)} маршрутов)", "",
      "Источник: `tools/api_inventory.py`. Право — `require_permission` или его алиас; «dep:» — проверка выполняется внутри зависимости (смотреть файл).", ""]
sections: dict[str, list] = {}
for r in rows:
    sections.setdefault("/".join(r["path"].split("/")[:4]), []).append(r)
for key in sorted(sections):
    md += [f"## `{key}`", "| Метод | Путь | Право | Файл |", "|---|---|---|---|"]
    for r in sections[key]:
        perm = ", ".join(r["permissions"]) or ("dep: " + ", ".join(r["deps"]) if r["deps"] else "—")
        md.append(f"| {r['method']} | `{r['path']}` | {perm} | {r['file']} |")
    md.append("")
Path(sys.argv[1]).with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
print(len(rows), "routes;", sum(1 for r in rows if not r["permissions"]), "without resolved permission")
