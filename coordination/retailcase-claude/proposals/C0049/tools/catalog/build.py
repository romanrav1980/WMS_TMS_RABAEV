"""C-0049/C0056: сборка role_catalog.json, roles/*.md, generated/*.md из данных каталога с проверками.

Запуск из proposals/C0049:  python tools/catalog/build.py
Проверки (ошибка = ненулевой код):
  * руководитель/заместитель ссылаются на существующие роли, дерево без циклов;
  * все 8 разделов рабочего места; 3–8 сценариев с типами normal/conflict/failure/handover;
  * экран — существующая raw/React страница; API — маршрут из инвентаризации; GAP — явная строка;
  * раздел «Допустимые команды» содержит только команды реестра C (метод/путь/право совпадают с маршрутом) или GAP;
  * право — проверяется API, есть в живом RIGHTS или объявлено в NEW_RIGHTS; группа ≤ 15, право ≤ 30 символов;
  * одна роль не держит обе стороны правила PERSON_RULES; пары ролей, конфликтующие при совмещении, выводятся в отчёт;
  * у KPI есть единица, поля, период, область и правило нулевого знаменателя.
Инвентаризация API статическая: спорные права подтверждены чтением маршрута (research/findings.md §4).
"""
import json, re, sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RAW = Path("C:/projects/TMS/wiki-raw/wms_admin_ui_reference")
sys.path.insert(0, str(HERE))
from sources import S, A, C  # noqa: E402
from model import FAMILIES, NEW_RIGHTS, ORACLE_RIGHTS, PERSON_RULES, OBJECT_RULES, SCOPES, DEVICES, WORKSPACE_STATUS, WAREHOUSE_PROFILE  # noqa: E402
import roles_network, roles_warehouse, roles_exec, roles_stock, roles_transport, roles_store, roles_support  # noqa: E402

MODULES = (roles_network, roles_warehouse, roles_exec, roles_stock, roles_transport, roles_store, roles_support)
ROLES = [r for m in MODULES for r in m.ROLES]
SECTIONS = {"home": "Главная", "queues": "Очереди и приоритеты", "filters": "Фильтры", "card": "Карточка объекта",
            "commands": "Допустимые команды", "history": "История и документы", "notify": "Уведомления и эскалации",
            "reports": "Отчётность"}
KINDS = {"normal": "обычный", "conflict": "дефицит/конфликт", "failure": "отказ/потеря связи", "handover": "передача"}

inv = json.load(open(ROOT / "research/api_inventory.json", encoding="utf-8"))["routes"]
route_perm = {(r["method"], r["path"]): set(r["permissions"]) for r in inv}
api_perms = {p for r in inv for p in r["permissions"]}
snap = Path("C:/projects/TMS/reports/retailcase/2026-10-13/claude/C0049/live_rights_snapshot.txt")
snap_text = snap.read_text(encoding="utf-8")
live = set(re.findall(r"([a-z0-9_]+)\(\d+\)", snap_text.split("ВСЕ ПРАВА")[1]))
live_groups = set(re.findall(r"'([A-Z_]+)': \d+", snap_text.split("Производственные группы")[1].split("\n")[0]))
app_tsx = Path("C:/projects/TMS/admin/wms_admin_frontend/src/App.tsx").read_text(encoding="utf-8")
errors: list[str] = []


def err(role, msg):
    errors.append(f"{role}: {msg}")


def resolve(ref: str, role: str, command: bool = False) -> dict:
    if ref.startswith("GAP:"):
        return {"kind": "gap", "text": ref[4:].strip()}
    tag, _, key = ref.partition(":")
    if command and tag != "c":
        err(role, f"в командах допустимы только c:/GAP, получено {ref}")
    if tag == "s" and key in S:
        kind, path, label = S[key]
        ok = (RAW / path).exists() if kind == "raw" else (f'page === "{path}"' in app_tsx) if kind == "react" else True
        if not ok:
            err(role, f"экран {key} ({path}) не найден")
        return {"kind": kind, "ref": path, "label": label}
    if tag == "a" and key in A:
        method, path = A[key]
        if (method, path) not in route_perm:
            err(role, f"API {method} {path} не найден")
        if method != "GET":
            err(role, f"a:{key} — изменяющий маршрут вне раздела команд")
        return {"kind": "api", "ref": f"{method} {path}"}
    if tag == "c" and key in C:
        method, path, perm, inp, res, retry = C[key]
        perms = route_perm.get((method, path))
        if perms is None:
            err(role, f"команда {key}: маршрут {method} {path} не найден")
        elif perm and not perm.startswith("native:") and perm not in perms:
            err(role, f"команда {key}: право {perm} не совпадает с маршрутом {sorted(perms)}")
        return {"kind": "command", "ref": f"{method} {path}", "perm": perm.replace("native:", "проверка native: ") if perm.startswith("native:") else perm, "input": inp, "result": res, "retry": retry}
    err(role, f"неизвестная ссылка {ref}")
    return {"kind": "unknown", "ref": ref}


def right_status(p: str) -> str:
    if p in api_perms:
        return "api" if p in live else "api_unassigned"
    return "oracle" if p in ORACLE_RIGHTS else "legacy" if p in live else "new" if p in NEW_RIGHTS else ""


ids = {r["id"] for r in ROLES}
if len(ids) != len(ROLES):
    errors.append("дубли id ролей")
out = []
for r in ROLES:
    rid = r["id"]
    for key in ("reports_to", "deputy"):
        if r.get(key) and r[key] not in ids:
            err(rid, f"{key}={r[key]} не существует")
    if r["family"] not in FAMILIES or r["scope"] not in SCOPES or r.get("workspace") not in WORKSPACE_STATUS:
        err(rid, "семейство/область/workspace вне справочника")
    for d in r["devices"]:
        if d not in DEVICES:
            err(rid, f"устройство {d}")
    if len(r["group"]) > 15:
        err(rid, f"группа {r['group']} > 15")
    if set(SECTIONS) - set(r["wp"]):
        err(rid, f"нет разделов {sorted(set(SECTIONS) - set(r['wp']))}")
    kinds = {k for k, _, _ in r["scenarios"]}
    if not (3 <= len(r["scenarios"]) <= 8) or set(KINDS) - kinds:
        err(rid, f"сценарии: {len(r['scenarios'])}, нет {sorted(set(KINDS) - kinds)}")
    perms = {}
    for level in ("read", "execute", "approve", "admin"):
        for p in r["perm"].get(level, []):
            st = right_status(p)
            if not st:
                err(rid, f"право {p} не найдено")
            if len(p) > 30:
                err(rid, f"право {p} > 30")
            perms[p] = {"level": level, "status": st or "unknown"}
    for a, b, why, _ in PERSON_RULES:
        if a in perms and b in perms:
            err(rid, f"PERSON SoD {a}+{b}: {why}")
    for k in r["kpi"]:
        for f in ("unit", "fields", "period", "scope", "zero"):
            if not k.get(f):
                err(rid, f"KPI {k['name']}: нет {f}")
    wp = {sec: [{"label": label, **resolve(ref, rid, sec == "commands")} for label, ref in r["wp"][sec]] for sec in SECTIONS if sec in r["wp"]}
    kpi = [{**k, "source": resolve(k["source"], rid)} for k in r["kpi"]]
    out.append({**{k: v for k, v in r.items() if k not in ("wp", "kpi", "perm", "scenarios")},
                "scenarios": [{"kind": k, "title": t, "steps": s} for k, t, s in r["scenarios"]],
                "workplace": wp, "kpi": kpi, "permissions": perms})

by_id = {r["id"]: r for r in out}
for r in out:
    seen, cur = set(), r
    while cur.get("reports_to"):
        if cur["id"] in seen:
            err(r["id"], "цикл подчинения")
            break
        seen.add(cur["id"])
        cur = by_id[cur["reports_to"]]
    r["subordinates"] = sorted(x["id"] for x in out if x.get("reports_to") == r["id"])
    for g in r.get("legacy_groups", []):
        if g not in live_groups:
            err(r["id"], f"legacy-группа {g} нет в снимке")

if errors:
    print("\n".join("ERROR " + e for e in errors))
    sys.exit(1)

# Совмещение: пары ролей, объединение прав которых нарушает PERSON_RULES.
conflicts = [{"roles": [a["id"], b["id"]], "rule": f"{x}+{y}", "why": why}
             for a, b in combinations(out, 2) for x, y, why, _ in PERSON_RULES
             if (x in a["permissions"] and y in b["permissions"]) or (y in a["permissions"] and x in b["permissions"])]
gaps = sorted({(r["id"], x["text"]) for r in out for sec in r["workplace"].values() for x in sec if x["kind"] == "gap"} |
              {(r["id"], k["source"]["text"]) for r in out for k in r["kpi"] if k["source"]["kind"] == "gap"})
catalog = {"schema": "retailcase.role_catalog/2", "generated_by": "tools/catalog/build.py", "date": "2026-10-14",
           "status_note": "Каталог — проект. Ролевые рабочие места не реализованы, кроме помеченных in_c0056; KPI не утверждены.",
           "families": FAMILIES, "scopes": SCOPES, "devices": DEVICES, "sections": SECTIONS, "scenario_kinds": KINDS,
           "workspace_status": WORKSPACE_STATUS, "warehouse_profile": WAREHOUSE_PROFILE,
           "sources": {k: {"kind": v[0], "ref": v[1], "label": v[2]} for k, v in S.items()},
           "commands": {k: dict(zip(("method", "path", "perm", "input", "result", "retry"), v)) for k, v in C.items()},
           "new_rights": NEW_RIGHTS, "oracle_rights": ORACLE_RIGHTS,
           "person_rules": [dict(zip(("a", "b", "why", "enforcement"), x)) for x in PERSON_RULES],
           "object_rules": [dict(zip(("object", "author_step", "check_step", "why", "enforcement"), x)) for x in OBJECT_RULES],
           "combination_conflicts": conflicts, "roles": out, "gaps": [{"role": a, "text": b} for a, b in gaps]}
(ROOT / "role_catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=1), encoding="utf-8")

STATUS = {"oracle": "проверяется native/Oracle (реализовано)", "api": "API, выдано группам", "api_unassigned": "API, сейчас ни у одной группы", "legacy": "legacy RIGHTS (desktop/ТСД)", "new": "**новое**"}
title = {r["id"]: r["title"] for r in out}


def src_text(x):
    if x["kind"] == "gap":
        return f"**GAP** — {x['text']}"
    if x["kind"] == "command":
        return f"`{x['ref']}` · право `{x['perm']}` · вход: {x['input']} · результат: {x['result']} · повтор: {x['retry']}"
    if x["kind"] == "api":
        return f"`{x['ref']}`"
    return f"{x['label']} (`{x['ref']}`)"


(ROOT / "roles").mkdir(exist_ok=True)
for old in (ROOT / "roles").glob("*.md"):
    old.unlink()
for r in out:
    L = [f"# {r['title']}", "",
         f"`{r['id']}` · {FAMILIES[r['family']]} · группа доступа (предложение): `{r['group']}`"
         + (f" · действующие legacy-группы: {', '.join('`' + g + '`' for g in r['legacy_groups'])}" if r.get("legacy_groups") else ""),
         f"Область назначения: {SCOPES[r['scope']]} · устройства: {', '.join(DEVICES[d] for d in r['devices'])} · рабочее место: **{WORKSPACE_STATUS[r['workspace']]}**", "",
         "## 1. Место в организации", "",
         f"- **Руководитель:** {title.get(r.get('reports_to'), '— (верх иерархии)')}",
         f"- **Подчинённые роли:** {', '.join(title[s] for s in r['subordinates']) or '—'}",
         f"- **Заместитель:** {title.get(r.get('deputy'), '—')}",
         f"- **Передача смены / замещение:** {r['handover']}",
         f"- **Эскалация:** {r['escalate']}", "", "**Отвечает за:**"] + [f"- {x}" for x in r["resp"]]
    if r.get("not_resp"):
        L += ["", "**Не вправе:**"] + [f"- {x}" for x in r["not_resp"]]
    L += ["", "## 2. События, решения, смена", "", f"**Смена:** {r['shift']}", "", "**Входящие события:**"] + [f"- {x}" for x in r["events"]]
    L += ["", "**Решения:**"] + [f"- {x}" for x in r["decisions"]] + ["", "**Сценарии:**", ""]
    L += [f"{i}. *{KINDS[s['kind']]}* — **{s['title']}.** {s['steps']}" for i, s in enumerate(r["scenarios"], 1)]
    L += ["", "## 3. Рабочее место", "", "| Раздел | Пункт | Источник / команда |", "|---|---|---|"]
    L += [f"| {name} | {x['label']} | {src_text(x)} |" for sec, name in SECTIONS.items() for x in r["workplace"].get(sec, [])]
    u = r["ui"]
    L += ["", "## 4. UI", "", f"- **Первый экран:** {u['first']}", f"- **Главное действие:** {u['main']}", f"- **Таблица:** {u['columns']}",
          f"- **Массовые операции:** {u['mass']}", f"- **Ввод:** {u['input']}", f"- **Ошибки, нет данных, нет связи:** {u['reliability']}"]
    L += ["", "## 5. KPI — предложение, не утверждено", "", "| Показатель | Ед. | Формула | Поля/события | Период · область | Знаменатель 0 | Источник |", "|---|---|---|---|---|---|---|"]
    L += [f"| {k['name']} | {k['unit']} | {k['formula']} | {k['fields']} | {k['period']} · {k['scope']} | {k['zero']} | {src_text(k['source'])} |" for k in r["kpi"]]
    L += ["", "## 6. Права", "", "| Уровень | Право | Статус |", "|---|---|---|"]
    L += [f"| {v['level']} | `{p}` | {STATUS[v['status']]} |" for p, v in r["permissions"].items()]
    L += ["", "**Разделение обязанностей:** " + ("; ".join(r["sod"]) if r.get("sod") else "общие правила permission_matrix.md"), ""]
    (ROOT / "roles" / f"{r['id']}.md").write_text("\n".join(L), encoding="utf-8")

# Сгенерированные таблицы для organization.md и permission_matrix.md.
gen = ROOT / "generated"
gen.mkdir(exist_ok=True)
tree = ["```mermaid", "flowchart TD"] + [f'  {r["id"]}["{r["title"]}"]' for r in out] + [f"  {r['reports_to']} --> {r['id']}" for r in out if r.get("reports_to")] + ["```"]
(gen / "org_tree.md").write_text("# Дерево подчинения (сгенерировано)\n\nПодчинение не передаёт права.\n\n" + "\n".join(tree) + "\n", encoding="utf-8")
M = ["# Маппинг ролей на права и области (сгенерировано)", "", "R — чтение, X — исполнение, A — подтверждение, M — администрирование. Статус права: API / API без групп / legacy / новое.", "",
     "| Роль | Группа | Область | Рабочее место | R | X | A | M |", "|---|---|---|---|---|---|---|---|"]
for r in out:
    cell = lambda lvl: ", ".join(f"`{p}`" + ("*" if v["status"] == "new" else "") for p, v in r["permissions"].items() if v["level"] == lvl) or "—"
    M.append(f"| {r['title']} | `{r['group']}` | {r['scope']} | {r['workspace']} | {cell('read')} | {cell('execute')} | {cell('approve')} | {cell('admin')} |")
M += ["", "\\* — новое право (NEW_RIGHTS).", "", "## Конфликты при совмещении ролей", ""]
M += [f"- {title[c['roles'][0]]} + {title[c['roles'][1]]}: `{c['rule']}` — {c['why']}" for c in conflicts] or ["- не обнаружено"]
(gen / "permission_mapping.md").write_text("\n".join(M) + "\n", encoding="utf-8")
(gen / "gaps.md").write_text("# GAP по ролям (сгенерировано)\n\n" + "\n".join(f"- `{a}` — {b}" for a, b in gaps) + "\n", encoding="utf-8")

print(f"OK: {len(out)} ролей, {sum(len(r['scenarios']) for r in out)} сценариев, "
      f"{sum(1 for r in out for x in r['workplace']['commands'] if x['kind'] == 'command')} команд с правом/повтором, {len(gaps)} GAP, "
      f"{len(conflicts)} конфликтов совмещения")
