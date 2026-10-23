create or replace package RRL_CASE_PICK_PAPER authid definer as
 -- Version of one CASE pick line for a paper sheet (BP15). Covers what makes an old sheet wrong: who is assigned (ASSIGNED_TO, not
 -- ASSIGNMENT_VERSION: RRL_CASE_ASSIGN_VERSION_GUARD bumps that on every status/start/resource change), the carrier,
 -- the line itself (cell, article, planned and already picked quantity, status, required scan mode) and the SKU receipt policy
 -- version that switches marking/weight-label scans. Other lines are not part of it: confirming one line keeps the rest of the
 -- sheet valid. The task status is not part of it either: starting the task after recovery is the normal next step, not a change of
 -- the paper. No new ledger, no stock write.
 function line_signature(p_line number)return varchar2;
 -- Refuses (confirmed refusal, not a retry class) when a sheet's version no longer matches. NULL expected = command without paper.
 procedure assert_expected(p_line number,p_expected varchar2);
end;
/
create or replace package body RRL_CASE_PICK_PAPER as
 function line_signature(p_line number)return varchar2 is j json_object_t:=json_object_t();t RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;v number;
 begin
  select*into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=p_line;
  select*into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID;
  j.put('task',t.CASE_PICK_TASK_ID);j.put('ware',t.WARE_ID);j.put('carrier',t.SSCC);j.put('assigned_to',t.ASSIGNED_TO);
  j.put('line',l.CASE_PICK_LINE_ID);j.put('pick_task',l.PICK_TASK_ID);
  j.put('article',l.ARTICUL);j.put('cell',l.CELL_CODE);j.put('planned',RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY));
  j.put('picked',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0)));j.put('status',l.STATUS);j.put('scan_mode',l.REQUIRED_SCAN_MODE);
  select max(POLICY_VERSION)into v from RRL_SKU_RECEIPT_POLICY where ARTICUL=l.ARTICUL;j.put('receipt_policy',v);
  return rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
 end;

 procedure assert_expected(p_line number,p_expected varchar2)is
 begin
  if p_expected is null then return;end if;
  if not regexp_like(p_expected,'^[A-F0-9]{64}$')or p_expected<>line_signature(p_line)then raise_application_error(-20886,'CASE_PAPER_LINE_CHANGED');end if;
 end;
end;
/
