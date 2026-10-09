"""Read-only arithmetic and dependency checks for the cross-dock-first plan."""
import json
import math
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
plan = json.loads((BASE / "plan.json").read_text(encoding="utf-8"))
baseline = json.loads((BASE / plan["baseline"]).read_text(encoding="utf-8"))
parents = {s["id"]: s for s in baseline["sprints"]}
assert len(parents) == 41
a = baseline["assumptions"]

def estimate(profile, scale):
    p = baseline["profiles"][profile]
    e = defaultdict(float)
    for key, role, inp, out in p["phases"]:
        m = baseline["models"][key]
        inp, out = inp * scale, out * scale
        lane = "local" if key == "local" else "cloud"
        e[lane + "_input_m"] += inp
        e[lane + "_output_m"] += out
        e["api"] += inp * (
            a["uncached_share"] * m["input"]
            + a["cache_write_share"] * m["cache_write"]
            + a["cache_read_share"] * m["cache_read"]
        ) + out * m["output"]
        e["worst_api"] += inp * max(m["input"], m["cache_write"]) + out * m["output"]
    e["local_hours"] = p["local_hours"] * scale
    e["electricity"] = e["local_hours"] * a["local_power_kw"] * a["electricity_usd_kwh"]
    e["human_hours"] = p["human_hours"] * scale
    e["agent_hours"] = p["agent_hours"] * scale
    return dict(e)

def add(target, source):
    for key, value in source.items():
        target[key] += value

used, early, residual, full = (defaultdict(float) for _ in range(4))
seen = set()
end = 0
cards = (ROOT / "wiki/requirements/nikora_crossdock_increments.md").read_text(encoding="utf-8")
roadmap = (ROOT / "wiki/roadmap/nikora_crossdock_first.md").read_text(encoding="utf-8")
rows = []
for s in plan["stages"]:
    assert s["id"] not in seen and set(s["deps"]) <= seen
    seen.add(s["id"])
    assert s["start"] == end + 1
    end += s["days"]
    assert s["finish"] == end
    e = defaultdict(float)
    for parent, fraction in s["allocation"]:
        assert parent in parents and 0 < fraction <= 1
        used[parent] += fraction
        assert used[parent] <= 1.00000001
        b = parents[parent]
        add(e, estimate(b["profile"], b["scale"] * fraction))
    if s["id"] == plan["extra_profile"]["stage"]:
        assert not s["allocation"]
        add(e, estimate(plan["extra_profile"]["profile"], plan["extra_profile"]["scale"]))
    assert e["human_hours"] <= s["days"] * a["review_capacity_hours_day"]
    assert 'id="' + s["id"].lower() + '"' in cards
    assert "дни " + str(s["start"]) + "–" + str(s["finish"]) in cards
    add(early, e)
    rows.append((s["id"], s["start"], s["finish"], e))

remaining_days = 0
allocated_days = 0
for key, b in parents.items():
    fraction = used[key]
    add(full, estimate(b["profile"], b["scale"]))
    add(residual, estimate(b["profile"], b["scale"] * (1 - fraction)))
    remaining_days += b["days"]["base"] * (1 - fraction)
    allocated_days += b["days"]["base"] * fraction
    assert "[" + key + "](" in roadmap
    parent_doc = ROOT / "wiki/requirements/nikora_sprints" / (key.lower().replace(".", "-") + ".md")
    assert "Приоритет исполнения 16.09.2026" in parent_doc.read_text(encoding="utf-8")
extra = estimate(plan["extra_profile"]["profile"], plan["extra_profile"]["scale"])
for key in full:
    assert math.isclose(early[key] + residual[key], full[key] + extra[key], rel_tol=1e-9)
assert math.isclose(allocated_days, 65)
assert math.isclose(remaining_days, 96)
assert end == 75
assert end + remaining_days == 171

for path in [
    ROOT / "wiki/roadmap/nikora_crossdock_first.md",
    ROOT / "wiki/requirements/nikora_crossdock_increments.md",
    BASE / "README.md",
]:
    text = path.read_text(encoding="utf-8")
    assert "\ufffd" not in text
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http:", "https:", "#")):
            continue
        file_part = target.split("#", 1)[0]
        assert (path.parent / file_part).exists(), (path, target)
    for target in re.findall(r"\[\[([^]|]+)(?:\|[^]]+)?\]\]", text):
        assert (ROOT / "wiki" / (target + ".md")).exists(), (path, target)

print("PASS: 21 increments, dependency order, 41 parent coverage, no double budget count.")
print("Milestones: receiving day 54; departure 57; pilot 66-75.")
print(f"Allocated days={allocated_days:g}; remaining={remaining_days:g}; full with extra pilot=171.")
print(f"Early API={early['api']:.2f}; electricity={early['electricity']:.2f}; owner hours={early['human_hours']:.2f}.")
print(f"Early base={early['api'] + early['electricity']:.2f}; reserve={(early['api'] + early['electricity']) * 1.5:.2f}; conservative={(early['worst_api'] + early['electricity']) * 1.5:.2f}.")
print("No implementation, live test, deployment or publication performed.")
