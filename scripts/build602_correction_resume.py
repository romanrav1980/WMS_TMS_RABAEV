from pathlib import Path
v=Path("scripts/case601_normative_correction.py").read_text(encoding="utf-8")
v=v.replace('if p.exists():raise SystemExit("601 retained; resume saved operations only")',
'''prior=json.loads(p.read_text(encoding="utf-8"))
assert prior.get("retired")and not prior.get("requests")and not prior.get("done"),"No completed facts may be recreated"
retired_actor=prior["actor"]''')
v=v.replace(' saved=dict(cost_operation_id=cost,',' saved=dict(retired_actors=[retired_actor],cost_operation_id=cost,')
Path("scripts/resume602_normative_correction.py").write_text(v,encoding="utf-8")
print("602 resumes original norm source after pre-API startup refusal; old actor stays retired, no earlier monetary expense existed.")
