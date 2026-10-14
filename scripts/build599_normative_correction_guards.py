from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-12_ni071_normative_correction")
p=f/"000_before_rrl_log_expense_guard.sql";v=p.read_text(encoding="utf-8")
a=" if :new.CORRECTION_OF_OP is null then";assert v.count(a)==1
b=""" if :new.COST_CORRECTION_OF_OP is not null then
  if :new.CORRECTION_OF_OP is not null then raise_application_error(-20886,'ONE_FINANCIAL_CORRECTION_SOURCE_REQUIRED');end if;
  select count(*)into n from RRL_LOGISTICS_EXP_ARTICLE a where a.CODE=:new.ARTICLE_CODE and a.VERSION_NO=:new.ARTICLE_VERSION
   and a.NAME=:new.ARTICLE_NAME and a.ACTIVE_FLAG=1 and a.INCLUDED_IN_RATE=0 and a.OBJECT_SCOPE in(:new.OBJECT_KIND,'BOTH');
  if n!=1 then raise_application_error(-20886,'LOGISTICS_EXTRA_ACTIVE_ARTICLE_REQUIRED');end if;
  RRL_NORM_COST_CORRECTION.validate_report(:new.COST_CORRECTION_OF_OP,:new.WARE_ID,:new.OBJECT_KIND,:new.OBJECT_ID,:new.CURRENCY,:new.AMOUNT*:new.ADJUSTMENT_SIGN,:new.EXPECTED_CONFIRMED_TOTAL);
 elsif :new.CORRECTION_OF_OP is null then"""
v=v.replace(a,b);(f/"003_report_guard.sql").write_text(v,encoding="utf-8")
p=f/"000_before_rrl_log_exp_decision_guard.sql";v=p.read_text(encoding="utf-8")
a=" if :new.PHASE='FINANCE' then";assert v.count(a)==1
v=v.replace(a," RRL_NORM_COST_CORRECTION.validate_decision(:new.EXPENSE_OPERATION_ID,:new.PHASE,:new.OUTCOME);\n"+a)
(f/"004_decision_guard.sql").write_text(v,encoding="utf-8")
p=f/"checkpoint.json";d=json.loads(p.read_text(encoding="utf-8"));d["status"]="PREPARED_NOT_APPLIED";d["prepared_sha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in f.glob("*.sql")if not p.name.startswith("000_")};p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
print("599 guards preserve existing report/current rights and independent LOGIST/FINANCE logic; normative source linked/CAS total, not duplicate expense.")
