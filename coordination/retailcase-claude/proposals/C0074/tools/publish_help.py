"""Публикация статей docs/help/authoring/*.md через /api/knowledge/commands (ARTICLE_SAVE → PUBLISH).
operation_id детерминирован от содержимого и версии: повтор после потери ответа воспроизводит ту же команду.
Пароль читается из AGENTS.md и не печатается. Использование: python publish_help.py <reason> <article.md>..."""
import base64, hashlib, json, re, sys, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
ROOT = "C:/projects/TMS"; API = "http://127.0.0.1:8088"
pw = re.search(r"PASS=([^`,)\s]+)", open(f"{ROOT}/AGENTS.md", encoding="utf-8").read()).group(1)
H = {"Authorization": "Basic " + base64.b64encode(f"admin:{pw}".encode()).decode(), "Content-Type": "application/json"}

def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, headers=H, data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, json.load(r)
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b"{}")

def parse(path):
    text = open(path, encoding="utf-8").read()
    head, body = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S).groups()
    meta = {}
    for line in head.splitlines():
        k, v = line.split(":", 1); v = v.strip()
        meta[k.strip()] = [x.strip() for x in v[1:-1].split(",") if x.strip()] if v.startswith("[") else v
    return meta, body.strip() + "\n"

def command(kind, payload):
    op = "help-" + hashlib.sha256(json.dumps([kind, payload], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:32]
    for attempt in range(3):  # сетевой сбой/5xx — исход неизвестен: тот же operation_id и то же тело
        try:
            st, res = call("POST", "/api/knowledge/commands", {"operation_id": op, "command_type": kind, "payload": payload})
        except OSError as e:
            st, res = 0, {"error": str(e)}
        if st and st < 500: return st, res
    return st, res

reason = sys.argv[1]
for path in sys.argv[2:]:
    meta, body = parse(path); aid = meta["article_id"]
    st, cur = call("GET", f"/api/knowledge/articles/{aid}")
    version = cur.get("version", 0) if st == 200 else 0
    if st == 200 and cur.get("body", "").strip() == body.strip() and cur.get("title") == meta["title"] and cur.get("summary") == meta["summary"] and cur.get("related") == meta["related"] and cur.get("status") == "PUBLISHED":
        print(aid, "без изменений, v", version); continue
    payload = {"article_id": aid, "space_id": meta["space_id"], "title": meta["title"], "summary": meta["summary"], "body": body,
               "related": meta["related"], "sources": meta["sources"], "required_permissions": meta["required_permissions"],
               "expected_version": version, "reason": reason}
    st, res = command("ARTICLE_SAVE", payload)
    if st != 200: print(aid, "ARTICLE_SAVE", st, res); continue
    st, res2 = command("PUBLISH", {"article_id": aid, "expected_version": res["version"], "reason": reason})
    print(aid, "сохранено v", res["version"], "→ PUBLISH", st, res2.get("version", res2))
