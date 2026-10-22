"""Build the shared-object patches of 2026-10-22_trade_topup_wave_adoption from exact current USER_SOURCE dumps.

usage: python build_adoption_migration.py <dump_dir>
Each change is an exact single-anchor replacement; a missing or repeated anchor aborts (drift is reviewed, never guessed).
Writes before_*.sql (rollback sources) and 003..006 patched objects.
"""
import pathlib
import sys

M = pathlib.Path(r"C:\projects\TMS\db\migrations\2026-10-22_trade_topup_wave_adoption")
dump = pathlib.Path(sys.argv[1])


def source(name: str, kind: str) -> str:
    return (dump / f"{name}.{kind}.sql").read_text(encoding="utf-8").replace("\r", "").rstrip() + "\n"


def ddl(text: str) -> str:
    return "create or replace " + text.lstrip() + "/\n"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        sys.exit(f"anchor not unique/absent ({text.count(old)}): {old[:100]!r}")
    return text.replace(old, new)


RELINK_SPEC = (" -- Top-up hold of one proposal becomes the wave's HARD in place: same RID, quantity, balance and units.\n"
               " procedure relink_topup(p_id number,p_proposal number,p_wave number,p_task number,p_plan number,p_plan_line number,\n"
               "  p_order number,p_customer number,p_actor varchar2);\n")
RELINK_BODY = """ procedure relink_topup(p_id number,p_proposal number,p_wave number,p_task number,p_plan number,p_plan_line number,
  p_order number,p_customer number,p_actor varchar2) is r RRL_STOCK_RESERVATION%rowtype;
 begin
  lock_identity(p_id);
  select * into r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  -- Only a TRADE_TOPUP hold of this very proposal changes its owner document; nothing else may be re-pointed.
  if r.RESERVATION_KIND!='HARD' or r.STATUS not in('ACTIVE','ALLOCATED') or r.SOURCE_DOC_TYPE is null or r.SOURCE_DOC_TYPE!='TRADE_TOPUP'
   or r.SOURCE_DOC_ID!=p_proposal or p_wave is null or p_task is null or p_plan_line is null then raise_application_error(-20869,'RESERVATION_CONFLICT');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',r.UID_PALLET));
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',r.UID_PALLET,r.CELL,p_id);
  update RRL_STOCK_RESERVATION set SOURCE_DOC_TYPE='PICK_WAVE',SOURCE_DOC_ID=p_wave,SOURCE_LINE_ID=p_task,RESERVATION_DOMAIN='PICKING',
   PICK_WAVE_ID=p_wave,PICK_PLAN_ID=p_plan,PICK_PLAN_LINE_ID=p_plan_line,CUSTOMER_ORDER_ID=p_order,CUSTOMER_ID=p_customer,
   RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=p_id and RESERVATION_VERSION=r.RESERVATION_VERSION;
  if sql%rowcount!=1 then raise_application_error(-20867,'VERSION_CONFLICT');end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
"""
ADOPT_HOLD = """ procedure adopt_hold(p_proposal number,pr RRL_PICK_RESERVATION%rowtype,p_wave number,p_ware number,p_new_id number,p_op varchar2,p_actor varchar2) is
  h RRL_TRADE_TOPUP_HOLD%rowtype;rid number;keys clob;
 begin
  select * into h from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=p_proposal and UID_PALLET=pr.PALLET_UID and CELL=pr.SOURCE_CELL_CODE and STATUS='ACTIVE' for update;
  if h.BASE_QTY<pr.RESERVED_QTY then raise_application_error(-20911,'TRADE_TOPUP_HOLD_CHANGED');end if;
  if h.BASE_QTY=pr.RESERVED_QTY then rid:=h.RESERVATION_ID;
  else
   -- Partial take-over on the same source: the shared HARD is split (never released and re-created); the exact units follow.
   RRL_STOCK_RESERVE_CORE.move_coverage(h.RESERVATION_ID,p_new_id,pr.PALLET_UID,pr.SOURCE_CELL_CODE,p_ware,pr.RESERVED_QTY,null,p_actor,rid);
   keys:=RRL_TRADE_TOPUP_ADOPT.split_units(h.RESERVATION_ID,pr.RESERVED_QTY);
   RRL_STOCK_UNIT_CORE.release_units(h.RESERVATION_ID,pr.RESERVED_QTY,keys,0);
   RRL_STOCK_UNIT_CORE.reserve_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,rid,pr.RESERVED_QTY,keys);
  end if;
  RRL_STOCK_RESERVE_CORE.relink_topup(rid,p_proposal,p_wave,pr.PICK_TASK_ID,pr.PICK_PLAN_ID,pr.PICK_PLAN_LINE_ID,pr.CUSTOMER_ORDER_ID,pr.CUSTOMER_ID,p_actor);
  RRL_TRADE_TOPUP_ADOPT.mark_adopted(h.RESERVATION_ID,rid,pr.RESERVED_QTY,p_proposal,p_wave,pr.PICK_TASK_ID,pr.PICK_PLAN_LINE_ID,p_op,p_actor);
 end;
"""

patches = {
    "003_reserve_core.sql": [
        ("RRL_STOCK_RESERVE_CORE", "PACKAGE", [("\nend;\n", "\n" + RELINK_SPEC + "end;\n")]),
        ("RRL_STOCK_RESERVE_CORE", "PACKAGE_BODY", [(" procedure restore_consumed(", RELINK_BODY + " procedure restore_consumed(")]),
    ],
    "004_picking.sql": [("RRL_PICKING_API", "PACKAGE_BODY", [
        ("    v_candidate_available number;\n", "    v_candidate_available number;\n    v_topup number;\n"),
        ("      v_remaining := v_requested_line_qty;\n",
         "      v_remaining := v_requested_line_qty;\n"
         "      -- A SAP top-up order row plans only on its own physical hold; a blocked one is refused explicitly.\n"
         "      v_topup:=case when v_release='ACTIVE'then RRL_TRADE_TOPUP_ADOPT.line_proposal(l.CUSTOMER_ORDER_ROW_ID)end;\n"
         "      if v_topup=-1 then raise_application_error(-20911,'TRADE_TOPUP_ADOPTION_CONDITIONS_NOT_MET');end if;\n"),
        ("'ALLOCATE',null,p.ARTICUL) is null)",
         "'ALLOCATE',case when v_topup>0 then RRL_TRADE_TOPUP_ADOPT.hold_rid(v_topup,r.UID_POLETA,r.CELL)end,p.ARTICUL) is null)\n"
         "           and (nvl(v_topup,0)<=0 or RRL_TRADE_TOPUP_ADOPT.hold_rid(v_topup,r.UID_POLETA,r.CELL) is not null)"),
        ("v_candidate_available := greatest(nvl(v_locked_remain, 0) - active_reserved_qty(c.UID_POLETA, l.ARTICUL, c.CELL), 0);",
         "v_candidate_available := case when v_topup>0 then RRL_TRADE_TOPUP_ADOPT.hold_free(v_topup,l.CUSTOMER_ORDER_ROW_ID,c.UID_POLETA,c.CELL)\n"
         "             else greatest(nvl(v_locked_remain, 0) - active_reserved_qty(c.UID_POLETA, l.ARTICUL, c.CELL), 0) end;"),
        ("v_reserved_by_other := v_reserved_by_other + (nvl(v_locked_remain, 0) - v_candidate_available);",
         "v_reserved_by_other := v_reserved_by_other + case when v_topup>0 then 0 else (nvl(v_locked_remain, 0) - v_candidate_available) end;"),
    ])],
    "005_wave_launch.sql": [("RRL_STOCK_WAVE_LAUNCH_CMD", "PACKAGE_BODY", [
        (" procedure compile_command(", ADOPT_HOLD + " procedure compile_command("),
        ("  if a.get_size=0 then raise_application_error(-20886,'WAVE_NO_SOFT_RESERVATIONS');end if;\n",
         "  RRL_TRADE_TOPUP_ADOPT.compile_wave(v_wave,r);\n  if a.get_size=0 then raise_application_error(-20886,'WAVE_NO_SOFT_RESERVATIONS');end if;\n"),
        ("units clob;pr RRL_PICK_RESERVATION%rowtype;", "units clob;pr RRL_PICK_RESERVATION%rowtype;v_topup number;"),
        ("   RRL_STOCK_ELIGIBILITY.assert_source(pr.PALLET_UID,pr.SOURCE_CELL_CODE,ware,pr.RESERVED_QTY,null,null,'ALLOCATE',null,pr.ARTICUL);\n",
         "   v_topup:=RRL_TRADE_TOPUP_ADOPT.task_proposal(pr.PICK_TASK_ID,pr.PALLET_UID,pr.SOURCE_CELL_CODE);\n"
         "   -- Its own hold counts as free for this task only (owner reservation), never as free stock for others.\n"
         "   RRL_STOCK_ELIGIBILITY.assert_source(pr.PALLET_UID,pr.SOURCE_CELL_CODE,ware,pr.RESERVED_QTY,null,null,'ALLOCATE',\n"
         "    case when v_topup is not null then RRL_TRADE_TOPUP_ADOPT.hold_rid(v_topup,pr.PALLET_UID,pr.SOURCE_CELL_CODE) end,pr.ARTICUL);\n"),
        ("   units:=RRL_WEIGHT_CHOICE_UNIT_READ.selected_units(",
         "   if v_topup is not null then adopt_hold(v_topup,pr,v.get_number('wave'),ware,x.get_number('reservation_id'),d.get_string('operation_id'),p_actor);\n"
         "   else\n   units:=RRL_WEIGHT_CHOICE_UNIT_READ.selected_units("),
        ("   RRL_STOCK_UNIT_CORE.reserve_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,x.get_number('reservation_id'),pr.RESERVED_QTY,units);\n",
         "   RRL_STOCK_UNIT_CORE.reserve_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,x.get_number('reservation_id'),pr.RESERVED_QTY,units);\n   end if;\n"),
    ])],
    "006_pick_context.sql": [("RRL_TRADE_PICK_CONTEXT", "PACKAGE_BODY", [
        ("  -- A SAP top-up order whose boxes are still held by its proposal must be taken over atomically, not reserved twice.\n"
         "  select count(*)into n from RRL_TRADE_ORDER_LINK tl join RRL_TRADE_TOPUP_PROPOSAL tp on tp.WARE_ID=tl.WARE_ID and tp.SAP_ORDER_ID=tl.EXTERNAL_ID\n"
         "   join RRL_TRADE_TOPUP_HOLD th on th.PROPOSAL_ID=tp.PROPOSAL_ID and th.STATUS='ACTIVE'where tl.CUSTOMER_ORDER_ID=g_line.CUSTOMER_ORDER_ID;\n"
         "  if n>0 then return 'TRADE_TOPUP_HOLD_ADOPTION_REQUIRED';end if;\n",
         "  -- A held SAP top-up order row may use only its own hold sources (taken over atomically at launch); others never.\n"
         "  declare g varchar2(100):=RRL_TRADE_TOPUP_ADOPT.gate(g_line.CUSTOMER_ORDER_ROW_ID,p_uid,p_cell);begin if g is not null then return g;end if;end;\n"),
    ])],
}

for file, units in patches.items():
    out = []
    for name, kind, edits in units:
        text = source(name, kind)
        suffix = "_spec" if kind == "PACKAGE" else ""
        (M / f"before_{name.lower()}{suffix}.sql").write_text(ddl(text), encoding="utf-8", newline="")
        for old, new in edits:
            text = once(text, old, new)
        out.append(ddl(text))
    (M / file).write_text("".join(out), encoding="utf-8", newline="")
print("built", sorted(p.name for p in M.iterdir()))
