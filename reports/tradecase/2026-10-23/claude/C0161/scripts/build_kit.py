"""C-0161: NOT_APPLIED kit 'topup after main loading started' from the live sources dumped READ ONLY in ../src (asserted edits)."""
import pathlib

S = pathlib.Path(__file__).resolve().parents[1] / "src"
D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_topup_after_load")
D.mkdir(parents=True, exist_ok=True)


def src(name, kind):
    return (S / f"{name}.{kind}.sql").read_text(encoding="utf-8").replace("\r\n", "\n")


def edit(text, pairs):
    for a, b in pairs:
        assert text.count(a) == 1, a[:100]
        text = text.replace(a, b)
    return text


def write(name, text):
    (D / name).write_text("create or replace " + text + "\n/\n", encoding="utf-8")


read_spec, read_body = src("RRL_TRADE_TOPUP_READ", "PACKAGE"), src("RRL_TRADE_TOPUP_READ", "PACKAGE_BODY")
api_body, cmd_body = src("RRL_TRADE_TOPUP_API", "PACKAGE_BODY"), src("RRL_TRADE_TOPUP_CMD", "PACKAGE_BODY")
for name, text in (("before_read_spec.sql", read_spec), ("before_read_body.sql", read_body), ("before_api_body.sql", api_body), ("before_cmd_body.sql", cmd_body)):
    write(name, text)

write("001_read_spec.sql", edit(read_spec, [(
    " function loading_started(p_ware number,p_trip varchar2)return number;\n",
    " function loading_started(p_ware number,p_trip varchar2)return number;\n"
    " -- C-0161: 1 once the trip's vehicle has departed (a departed load fact or an applied departure of its native task); a top-up\n"
    " -- may still be saved/confirmed while the main load is partly or fully in the vehicle, never after departure.\n"
    " function departed(p_ware number,p_trip varchar2)return number;\n")]))

write("002_read_body.sql", edit(read_body, [
    ("  return sha(acc);\n exception when no_data_found then raise_application_error(-20911,'TRADE_TOPUP_TRIP_REQUIRED');\n end;\n",
     "  -- C-0161: the physical loading of the bound native task is part of the basis: every LOAD/UNLOAD/DEPART, a changed content version\n"
     "  -- or another vehicle on the native task makes an earlier calculation stale. The ordered load history is folded into a chained\n"
     "  -- SHA-256 (fixed 64 chars per task, every transition included, nothing truncated), so any history length fits acc.\n"
     "  for t in(select l.NATIVE_TASK_ID,upper(trim(tt.TRANSPORT))TRANSPORT from RRL_TRADE_TRIP_LINK l join RRL_TRANSPORT_TASK tt on tt.ID=l.NATIVE_TASK_ID\n"
     "    where l.WARE_ID=p_ware and l.TRIP_ID=p_trip)loop\n"
     "   declare lh varchar2(64):='-';cnt number:=0;begin\n"
     "    for f in(select LOAD_OPERATION_ID,STATUS,CONTENT_VERSION from RRL_TT_HU_LOAD_FACT where TT_ID=t.NATIVE_TASK_ID order by LOAD_OPERATION_ID)loop\n"
     "     lh:=sha(lh||'|L:'||f.LOAD_OPERATION_ID||':'||f.STATUS||':'||f.CONTENT_VERSION);cnt:=cnt+1;\n"
     "    end loop;\n"
     "    acc:=acc||'|T:'||t.NATIVE_TASK_ID||':'||t.TRANSPORT||':'||cnt||':'||lh;\n"
     "   end;\n"
     "  end loop;\n"
     "  return sha(acc);\n exception when no_data_found then raise_application_error(-20911,'TRADE_TOPUP_TRIP_REQUIRED');\n end;\n"),
    (" function need_confirmed_boxes(",
     " function departed(p_ware number,p_trip varchar2)return number is n number;\n"
     " begin\n"
     "  select count(*)into n from RRL_TRADE_TRIP_LINK l\n"
     "   where l.WARE_ID=p_ware and l.TRIP_ID=p_trip and(exists(select 1 from RRL_TT_HU_LOAD_FACT f where f.TT_ID=l.NATIVE_TASK_ID and f.STATUS='DEPARTED')\n"
     "    or exists(select 1 from RRL_TT_VEHICLE_SOURCE s join RRL_STOCK_OPERATION o on o.OPERATION_ID=s.DEPARTURE_OPERATION_ID\n"
     "     where s.TT_ID=l.NATIVE_TASK_ID and o.STATE='APPLIED'and o.COMMAND_TYPE='TRIP_DEPART'));\n"
     "  return least(n,1);\n"
     " end;\n\n"
     " function need_confirmed_boxes("),
]))

write("003_api_body.sql", edit(api_body, [(
    "  if RRL_TRADE_TOPUP_READ.loading_started(ware,trip)=1 then fail('TOPUP_LOADING_ALREADY_STARTED');end if;\n",
    "  -- C-0161: partly or fully loaded main cargo is allowed (its facts are in the basis above); a departed trip is not.\n"
    "  if RRL_TRADE_TOPUP_READ.departed(ware,trip)=1 then fail('TOPUP_TRIP_DEPARTED');end if;\n")]))

write("004_cmd_body.sql", edit(cmd_body, [
    ("  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRADE_TOPUP_PROPOSAL',RRL_STOCK_PLAN_HELPER.decimal_text(p.PROPOSAL_ID));\n",
     "  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRADE_TOPUP_PROPOSAL',RRL_STOCK_PLAN_HELPER.decimal_text(p.PROPOSAL_ID));\n"
     "  -- C-0161: the same native transport row as LOAD and DEPART, so a confirmation never lands after a departure or between a load\n"
     "  -- fact and its basis check.\n"
     "  for t in(select NATIVE_TASK_ID from RRL_TRADE_TRIP_LINK where WARE_ID=p.WARE_ID and TRIP_ID=p.TRIP_ID)loop\n"
     "   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.NATIVE_TASK_ID));\n"
     "  end loop;\n"),
    ("  if RRL_TRADE_TOPUP_READ.loading_started(p.WARE_ID,p.TRIP_ID)=1 then fail('TOPUP_LOADING_ALREADY_STARTED');end if;\n",
     "  -- C-0161: loaded main cargo is in the capacity basis checked next; only a departed trip refuses here (under the transport row lock).\n"
     "  if RRL_TRADE_TOPUP_READ.departed(p.WARE_ID,p.TRIP_ID)=1 then fail('TOPUP_TRIP_DEPARTED');end if;\n"
     "  -- C-0161: with main cargo already loaded the planned departure must still be ahead now, at confirmation (not only at calculation/save).\n"
     "  -- The time is the accepted TRIP's planned_departure_at, ISO-8601 with offset as validated on receipt; unreadable = refused.\n"
     "  if RRL_TRADE_TOPUP_READ.loading_started(p.WARE_ID,p.TRIP_ID)=1 then\n"
     "   declare dep timestamp with time zone;begin\n"
     "    select json_value(BODY_JSON,'$.planned_departure_at'returning timestamp with time zone error on error)into dep\n"
     "     from RRL_TRADE_DOCUMENT where WARE_ID=p.WARE_ID and ENTITY_TYPE='TRIP'and EXTERNAL_ID=p.TRIP_ID and STATUS='ACCEPTED';\n"
     "    if dep is null or dep<=systimestamp then fail('TOPUP_DEPARTURE_TIME_PASSED');end if;\n"
     "   exception when no_data_found then fail('TRADE_TOPUP_TRIP_REQUIRED');\n"
     "    when others then if sqlcode=-20911 then raise;end if;fail('TOPUP_DEPARTURE_TIME_INVALID');\n"
     "   end;\n"
     "  end if;\n"),
]))
print("kit written to", D)
