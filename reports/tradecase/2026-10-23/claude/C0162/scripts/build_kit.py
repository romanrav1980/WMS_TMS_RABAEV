"""C-0162: NOT_APPLIED kit 'current rights for the common pool, replay included' from live sources dumped READ ONLY in ../src."""
import pathlib

S = pathlib.Path(__file__).resolve().parents[1] / "src"
D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_pool_access")
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


cmd_spec, cmd_body, post_body = src("RRL_STOCK_POOL_CMD", "PACKAGE"), src("RRL_STOCK_POOL_CMD", "PACKAGE_BODY"), src("RRL_STOCK_POSTING_API", "PACKAGE_BODY")
for name, text in (("before_pool_cmd_spec.sql", cmd_spec), ("before_pool_cmd_body.sql", cmd_body), ("before_posting_api_body.sql", post_body)):
    write(name, text)

write("001_pool_cmd_spec.sql", edit(cmd_spec, [(
    " procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);\nend;",
    " procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);\n"
    " -- C-0162: today's rights for a pool command, called by the runner before the committed-replay branch: the warehouse right\n"
    " -- (RRL_ACCESS_API: GLOBAL_ADMIN, legacy group of that warehouse, current scoped assignment) and, for a recorded trade plan, operate\n"
    " -- on the owner of every class it promised. A stored receipt is never shown to someone who could not issue the command now.\n"
    " procedure assert_access(p_request clob,p_actor varchar2);\nend;")]))

write("002_pool_cmd_body.sql", edit(cmd_body, [
    (" procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is\n",
     " procedure require_edit(p_actor varchar2,p_ware number)is\n"
     " begin\n"
     "  if p_ware is null or RRL_ACCESS_API.allowed(p_actor,'stock_reservation_edit','WAREHOUSE',to_char(p_ware))<>1 then\n"
     "   raise_application_error(-20882,'POOL_ALLOCATION_FORBIDDEN');end if;\n"
     " end;\n"
     " -- Owners of the classes a recorded trade plan used (its own resolved domain, not today's quantities).\n"
     " procedure require_plan_owners(p_domain json_object_t,p_actor varchar2,p_ware number)is\n"
     "  s json_object_t;cls json_array_t;src json_object_t;keys json_key_list;c json_object_t;\n"
     " begin\n"
     "  if not p_domain.has('sources')then return;end if;\n"
     "  s:=json_object_t.parse(p_domain.get_clob('snapshot'));cls:=s.get_array('classes');src:=p_domain.get_object('sources');\n"
     "  if cls is null or src is null or src.get_size=0 then return;end if;  -- an all-zero plan promised no class (as the execute guard)\n"
     "  keys:=src.get_keys;\n"
     "  for i in 0..cls.get_size-1 loop\n"
     "   c:=treat(cls.get(i) as json_object_t);\n"
     "   for k in 1..keys.count loop\n"
     "    if src.get_object(keys(k)).has(c.get_string('key'))and nonnegative(src.get_object(keys(k)).get_string(c.get_string('key')))>0 then\n"
     "     RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,c.get_string('owner'),1);exit;\n"
     "    end if;\n"
     "   end loop;\n"
     "  end loop;\n"
     " end;\n"
     " procedure assert_access(p_request clob,p_actor varchar2)is\n"
     "  d json_object_t:=json_object_t.parse(p_request);ware number:=d.get_object('source').get_number('warehouse');wire clob;\n"
     "  op varchar2(100):=d.get_string('operation_id');  -- JSON object methods never inside SQL (ORA-40573)\n"
     " begin\n"
     "  require_edit(p_actor,ware);\n"
     "  begin select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;\n"
     "  exception when no_data_found then return;end;  -- a new command: execute checks the owners of the plan it is about to post\n"
     "  if wire is not null then require_plan_owners(json_object_t.parse(wire).get_object('domain'),p_actor,ware);end if;\n"
     " end;\n"
     " procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is\n"),
    ("  if RRL_HAS_WRIGHT(p_actor,'stock_reservation_edit')!=1 then raise_application_error(-20882,'POOL_ALLOCATION_FORBIDDEN');end if;\n"
     "  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;\n"
     "  v:=json_object_t.parse(wire).get_object('domain');ware:=v.get_number('warehouse');article:=v.get_string('article');\n",
     "  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;\n"
     "  v:=json_object_t.parse(wire).get_object('domain');ware:=v.get_number('warehouse');article:=v.get_string('article');\n"
     "  require_edit(p_actor,ware);  -- C-0162: the warehouse of this plan, by current assignment/legacy group/GLOBAL_ADMIN\n"),
]))

anchor = ("  if g_kind in('WAVE_LAUNCH','WAVE_RESERVE_SOURCES','WAVE_EXECUTION_FINISH','WAVE_PICK_RELEASE')then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;  \n"
          "  if g_kind='CASE_PALLET_TYPE_CHANGE'then")
write("003_posting_api_body.sql", edit(post_body, [(
    anchor,
    "  if g_kind in('WAVE_LAUNCH','WAVE_RESERVE_SOURCES','WAVE_EXECUTION_FINISH','WAVE_PICK_RELEASE')then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;  \n"
    "  if g_kind='RESERVATION_ALLOCATE_POOL'then RRL_STOCK_POOL_CMD.assert_access(p_request,p_actor);end if;  -- C-0162: current rights before replay\n"
    "  if g_kind='CASE_PALLET_TYPE_CHANGE'then")]))
print("kit written to", D)
