from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/public.py");s=p.read_text(encoding="utf-8")
s+="\nfrom .api.day_review_routes import router as day_review_router\nfrom .contracts_day_reviews import day_reviews_service,DayReviewsPort\nfrom .infrastructure.day_reviews import DayReviews\n\ndef build_day_reviews(gateway: Any) -> DayReviewsPort:\n    return DayReviews(gateway)\n"
out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8");s+="\nfrom .modules.finance.public import day_review_router,day_reviews_service,build_day_reviews\napp.include_router(day_review_router)\napp.dependency_overrides[day_reviews_service]=lambda: build_day_reviews(OracleGateway())\n";out[str(p)]=s
p=Path("db/migrations/2026-10-11_ni072_review/002_api.sql");s=p.read_text(encoding="utf-8").replace("v_lock boolean:=false;","v_lock boolean:=false;v_saved boolean:=false;")
s=s.replace("savepoint RRL_DAY_REVIEW269;","savepoint RRL_DAY_REVIEW269;v_saved:=true;")
s=s.replace("if material.get_number('warehouse_id')","if not material.has('warehouse_id')or not material.has('business_date')or not material.has('timezone_region')or not material.has('consistent_snapshot')or not material.has('day_closed')then raise_application_error(-20886,'DAY_REVIEW_CAPTURE_FIELDS_REQUIRED');end if;\n  if material.get_number('warehouse_id')")
s=s.replace("g_tx:=null;if v_lock then","g_tx:=null;if v_saved then rollback to RRL_DAY_REVIEW269;end if;if v_lock then")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
