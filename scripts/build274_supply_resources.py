from pathlib import Path
import json
out={};root="db/migrations/2026-10-11_ni011_supply_resources/"
p=Path("db/migrations/2026-10-11_ni011_exact_source/001_scope.sql");before=p.read_text(encoding="utf-8")
signature=" procedure begin_supply(p_actor varchar2,p_ware number,p_sender varchar2,p_order varchar2,p_message varchar2);\n"
s=before.replace(" procedure end_source;",signature+" procedure end_source;",1)
pos=s.index(" procedure end_source is")
body=""" procedure begin_supply(p_actor varchar2,p_ware number,p_sender varchar2,p_order varchar2,p_message varchar2)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();
  declared_id varchar2(32);current_id varchar2(32);v_nak number;old_ware number;n number:=0;
 begin
  assert_scope(p_actor,'sap_supply_import',p_ware);
  if p_sender is null or lengthb(p_sender)>100 or p_order is null or lengthb(p_order)>20 or p_message is null or lengthb(p_message)>100 then raise_application_error(-20886,'SUPPLY_SOURCE_RESOURCE_INPUT_BOUND');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',4);
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);
  RRL_STOCK_PLAN_HELPER.anchor(r,20,'SUPPLY.SOURCE',p_sender,p_order);
  RRL_STOCK_PLAN_HELPER.anchor(r,20,'SUPPLY.MESSAGE',p_sender,p_message);
  begin
   select ORDER_ID,NAKLAD_ID,WARE_ID into declared_id,v_nak,old_ware from RRL_SAP_SUPPLY_ORDER where SENDER=p_sender and ORDER_NUMBER=p_order;
   assert_scope(p_actor,'sap_supply_import',old_ware);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_SUPPLY_ORDER',declared_id);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(v_nak));
   for x in(select LINE_NUMBER,ROW_ID from RRL_SAP_SUPPLY_LINE where ORDER_ID=declared_id order by LINE_NUMBER fetch first 1001 rows only)loop
    n:=n+1;if n>1000 then raise_application_error(-20886,'SUPPLY_SOURCE_LINE_RESOURCE_BOUND_1000');end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_SUPPLY_LINE',declared_id||':'||x.LINE_NUMBER);
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(x.ROW_ID));
   end loop;
  exception when no_data_found then null;end;
  RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  assert_scope(p_actor,'sap_supply_import',p_ware);
  begin select ORDER_ID,WARE_ID into current_id,old_ware from RRL_SAP_SUPPLY_ORDER where SENDER=p_sender and ORDER_NUMBER=p_order;
   assert_scope(p_actor,'sap_supply_import',old_ware);
  exception when no_data_found then current_id:=null;end;
  if nvl(current_id,'~')!=nvl(declared_id,'~')then raise_application_error(-20886,'SUPPLY_SOURCE_REPLAN_REQUIRED');end if;
 exception when others then RRL_STOCK_LOCK_API.clear_plan;raise;
 end;
"""
s=s[:pos]+body+s[pos:]
out[root+"000_before.sql"]=before;out[root+"001_scope.sql"]=s
out[root+"apply.sql"]="@001_scope.sql\nalter package RRL_SAP_STORE_ADMISSION_API compile body;\n"
out[root+"rollback.sql"]="@000_before.sql\nalter package RRL_SAP_STORE_ADMISSION_API compile body;\n"
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/supply_scope.py");s=p.read_text(encoding="utf-8").replace("warehouse: int) -> Iterator[Any]","warehouse: int,sender: str,order: str,message: str) -> Iterator[Any]")
s=s.replace('cur.callproc("RRL_STORE_ORDER_SCOPE.begin_source",[actor,"sap_supply_import",warehouse,None])','cur.callproc("RRL_STORE_ORDER_SCOPE.begin_supply",[actor,warehouse,sender,order,message])')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py");s=p.read_text(encoding="utf-8")
s=s.replace("    def receive(self, raw: bytes, actor: str) -> dict:\n        order = read_supply_order(raw)",'''    def receive(self, raw: bytes, actor: str) -> dict:
        for attempt in range(2):
            try:
                return self._receive(raw, actor)
            except oracledb.DatabaseError as exc:
                if "SUPPLY_SOURCE_REPLAN_REQUIRED" not in str(exc):
                    raise
                if attempt == 1:
                    raise IdocConflict("Supply source changed; repeat the same XML") from exc
        raise RuntimeError("Unreachable supply retry")

    def _receive(self, raw: bytes, actor: str) -> dict:
        order = read_supply_order(raw)''')
s=s.replace('supply_transaction(self.gateway,actor,order["warehouse_id"])','supply_transaction(self.gateway,actor,order["warehouse_id"],order["sender"],order["order_number"],order["message_id"])')
s=s.replace('            # Legacy headers have no source identity constraint. Serialize source mapping only.\n            cur.execute("lock table RRL_SAP_SUPPLY_ORDER in share row exclusive mode wait 3")\n','')
s=s.replace("NAKLAD_ID,REVISION,PAYLOAD_HASH from RRL_SAP_SUPPLY_ORDER","NAKLAD_ID,REVISION,PAYLOAD_HASH,WARE_ID from RRL_SAP_SUPPLY_ORDER",1).replace("ORDER_NUMBER=:n for update","ORDER_NUMBER=:n for update wait 3",1)
s=s.replace('            if old and order["revision"]','            if old:\n                assert_supply_scope(cur,actor,old[4])\n            if old and order["revision"]',1)
s=s.replace('order["lines"], previous_lines)','order["lines"], previous_lines,order["sender"])',1)
s=s.replace('lines: list[dict], previous: dict) -> None:','lines: list[dict], previous: dict,sender: str) -> None:',1)
s=s.replace('            cur.execute("select ACTICUL from RRL_ARTICULS','            if master[2] != sender:\n                raise ValueError("Supply article belongs to another SAP sender")\n            cur.execute("select ACTICUL from RRL_ARTICULS',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
