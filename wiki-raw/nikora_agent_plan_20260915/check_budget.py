"""Validate the planning estimate, not runtime implementation. No network calls."""
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
data = json.loads((BASE / "budget.json").read_text(encoding="utf-8"))
a, models, profiles = data["assumptions"], data["models"], data["profiles"]
assert "local_full_rate_usd_hour" not in a
assert "human_rate_example_usd_hour" not in a
assert math.isclose(a["cache_read_share"] + a["cache_write_share"] + a["uncached_share"], 1)
totals = defaultdict(float)
seen = set()
rows = []
main = (ROOT / "wiki/roadmap/nikora_agent_delivery_plan.md").read_text(encoding="utf-8")
catalog = (ROOT / "wiki/requirements/nikora_sprints/index.md").read_text(encoding="utf-8")
assert Counter(s["kind"] for s in data["sprints"]) == {
    "setup": 1, "architecture": 10, "functional": 28, "pilot": 2
}

for s in data["sprints"]:
    assert s["id"] not in seen, s["id"]
    assert set(s["deps"]) <= seen, (s["id"], "dependency not ready")
    seen.add(s["id"])
    profile, scale = profiles[s["profile"]], s["scale"]
    e = defaultdict(float)
    for model_key, role, inp, out in profile["phases"]:
        m = models[model_key]
        inp, out = inp * scale, out * scale
        lane = "local" if model_key == "local" else "cloud"
        e[lane + "_input_m"] += inp
        e[lane + "_output_m"] += out
        e["api_usd"] += inp * (
            a["uncached_share"] * m["input"]
            + a["cache_write_share"] * m["cache_write"]
            + a["cache_read_share"] * m["cache_read"]
        ) + out * m["output"]
        e["api_no_cache_usd"] += inp * m["input"] + out * m["output"]
        e["api_all_write_usd"] += inp * max(m["input"], m["cache_write"]) + out * m["output"]
    for field in ("local_hours", "agent_hours", "human_hours"):
        e[field] = profile[field] * scale
    e["electricity_usd"] = e["local_hours"] * a["local_power_kw"] * a["electricity_usd_kwh"]
    e["total_marginal_usd"] = e["total_usd"] = e["api_usd"] + e["electricity_usd"]
    e["reserve_budget_usd"] = e["total_usd"] * a["reserve_multiplier"]
    e["conservative_budget_usd"] = (e["api_all_write_usd"] + e["electricity_usd"]) * a["reserve_multiplier"]
    days = s["days"]
    assert 0 < days["low"] <= days["base"] <= days["high"]
    assert e["human_hours"] <= days["base"] * a["review_capacity_hours_day"], s["id"]
    start, finish = int(totals["days"]) + 1, int(totals["days"]) + days["base"]
    slug = s["id"].lower().replace(".", "-")
    card = ROOT / "wiki/requirements/nikora_sprints" / (slug + ".md")
    text = card.read_text(encoding="utf-8")
    assert f"{start}–{finish}" in text, (s["id"], "calendar mismatch")
    assert f"API: $" + format(e["api_usd"], ".2f") in text, (s["id"], "API mismatch")
    assert "Денежные расходы всего: $" + format(e["total_usd"], ".2f") in text
    assert "резервом 50%: $" + format(e["reserve_budget_usd"], ".2f") in text
    assert "$" + format(e["conservative_budget_usd"], ".2f") in text
    row = next(line for line in main.splitlines() if line.startswith("| [" + s["id"] + "]("))
    assert "| " + format(e["total_usd"], ".2f") + " | " + format(e["reserve_budget_usd"], ".2f") + " |" in row
    assert f"]({slug}.md)" in catalog
    for key, val in e.items():
        totals[key] += val
    totals["days"] += days["base"]
    totals["days_low"] += days["low"]
    totals["days_high"] += days["high"]
    rows.append((s["id"], e))

for key, expected in data["expected_totals"].items():
    assert math.isclose(totals[key], expected, rel_tol=1e-9, abs_tol=1e-8), (key, totals[key], expected)
assert set(totals) == set(data["expected_totals"])
docs = [
    ROOT / "wiki/roadmap/nikora_agent_delivery_plan.md",
    ROOT / "wiki/runbooks/nikora_agent_launch.md",
    ROOT / "wiki/requirements/nikora_sprint_contract.md",
    ROOT / "wiki/sources/nikora_agents_20260915.md",
    *sorted((ROOT / "wiki/requirements/nikora_sprints").glob("*.md")),
    *sorted(BASE.glob("*.md")),
]
for path in docs:
    text = path.read_text(encoding="utf-8")
    assert "AI/TCO" not in text and "local_full_rate" not in text, path
    assert "\ufffd" not in text, path
    for line in text.splitlines():
        assert line == line.rstrip(), (path, "trailing whitespace")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http:", "https:", "#", "mailto:")):
            continue
        target = target.split("#", 1)[0].replace("%20", " ")
        if not target or "<" in target:
            continue
        assert (path.parent / target).exists(), (path, "missing link", target)
    for target in re.findall(r"\[\[([^]|]+)(?:\|[^]]+)?\]\]", text):
        assert (ROOT / "wiki" / (target + ".md")).exists(), (path, target)
print("PASS: 41 cards; 10 architecture + 28 functional + S0/P1/P2.")
print("PASS: dependency order, calendar, all card/main budgets, local links.")
print("Costs: cloud API + electricity ONLY; human time is hours, not USD.")
for key, value in totals.items():
    print(f"{key}: {value:.6f}")
print("No functional test, device measurement, model call or installation performed.")

