package RRL_TRADE_TOPUP_ADOPT authid definer as
 -- Proposal whose physical hold this native order row may take over: null — not a held top-up order (ordinary path);
 -- -1 — a top-up order whose proposal is not SAP_ACCEPTED or whose SAP order/updated TRIP/terms/units do not match (blocked).
 function line_proposal(p_row number)return number;
 -- Pick-context gate: null allows; otherwise the reason the source may not serve this order row.
 function gate(p_row number,p_uid varchar2,p_cell varchar2)return varchar2;
 function hold_rid(p_proposal number,p_uid varchar2,p_cell varchar2)return number;
 -- Own ACTIVE hold on the source minus this row's open SOFT projections there: what planning may still project.
 function hold_free(p_proposal number,p_row number,p_uid varchar2,p_cell varchar2)return number;
 -- Launch: proposal for the task's row with an ACTIVE hold on the task source, null for ordinary tasks; raises when blocked.
 function task_proposal(p_task number,p_uid varchar2,p_cell varchar2)return number;
 procedure compile_wave(p_wave number,p_resources in out nocopy json_array_t);
 function split_units(p_hold number,p_qty number)return clob;
 procedure mark_adopted(p_hold number,p_rid number,p_qty number,p_proposal number,p_wave number,p_task number,p_line number,p_op varchar2,p_actor varchar2);
end;