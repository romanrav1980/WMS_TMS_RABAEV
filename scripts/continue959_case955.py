from pathlib import Path
src=Path("scripts/resume956_case_wait.py").read_text(encoding="utf-8")
src=src.replace(' CasePickService(OracleGateway()).ensure_wave_case_pick_tasks(wave,"admin")',' CasePickService(OracleGateway()).ensure_wave_case_pick_tasks(wave,"admin")\n from app.modules.inventory.infrastructure.replenishment_continuation import ReplenishmentContinuation\n from app.modules.resources.public import sync_existing_wave_tasks\n ReplenishmentContinuation(OracleGateway(),sync_existing_wave_tasks).reconcile(ware,"admin")')
exec(compile(src,"retained955_continuation","exec"))
