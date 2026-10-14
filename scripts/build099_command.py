from pathlib import Path
import json
p=Path("db/migrations/2026-10-08_stock_posting_core/403_checkpoint_before_deadline.sql")
s=p.read_text(encoding="utf-8-sig")
needle="exception when no_data_found then raise_application_error(-20886,'TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED');"
# Source checkpoint names the original rule exactly.
needle="exception when no_data_found then raise_application_error(-20886,'TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED');" if needle in s else "exception when no_data_found then raise_application_error(-20886,'TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED');"
# Inspect the actual source instead of silently omitting the hook.
actual="exception when no_data_found then raise_application_error(-20886,'TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED');"
if actual not in s:
 actual="exception when no_data_found then raise_application_error(-20886,'TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED');"
# Existing source rule uses original holder/trip/offer.
line=next(line for line in s.splitlines() if "TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED" in line or "TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER" in line) if "TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER" in s else next(line for line in s.splitlines() if "TARE_ORIGINAL_HOLDER_TRIP_OR_OFFER_REQUIRED" in line)
s=s.replace(line,''' if kind='TARE_ACCEPT' and v_to_kind='STORE' then
  declare policy_domain json_object_t;begin RRL_STOCK_TARE_POLICY.describe_store(v_to_id,policy_domain);p_domain.put('return_policy',policy_domain);end;
 end if;
'''+line,1)
needle="p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;"
assert needle in s
s=s.replace(needle,"if kind='TARE_ACCEPT' and v.get_string('to_kind')='STORE' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_DELIVERY_POLICY',p_operation);end if;\n "+needle,1)
needle="values(op,v_offer,v_qty,v_offered-v_qty,p_actor);"
assert needle in s
s=s.replace(needle,needle+"\n   if v_to_kind='STORE' then RRL_STOCK_TARE_POLICY.record_delivery(op,v.get_object('return_policy'));end if;",1)
print(json.dumps({"db/migrations/2026-10-10_ni063_tare_deadlines/003_tare_command.sql":s},ensure_ascii=True))
