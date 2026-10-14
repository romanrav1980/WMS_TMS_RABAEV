from pathlib import Path
root=Path('db/migrations/2026-10-14_ni051_scoped_quality')
def old(name):return '\n'.join(x for x in (root/'saved'/name).read_text(encoding='utf-8').splitlines() if x.strip())+'\n'
def change(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
s=old('RRL_STOCK_QC_POLICY_PACKAGE_BODY.sql')
s=change(s,"d json_object_t:=json_object_t.parse(p_domain);case_id number:=d.get_number('case_task');required number;", "d json_object_t:=json_object_t.parse(p_domain);case_id number:=d.get_number('case_task');required number;policy json_object_t;")
s=change(s,"  settings(d.get_number('warehouse'),p_mode,p_independent);", "  policy:=json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(p_domain));p_mode:=policy.get_string('mode');p_independent:=policy.get_number('independent');")
s=change(s,"  select nvl(max(OUTGOING_QC_SAMPLE_PERCENT),0) into p_percent from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=v_ware;", "  p_percent:=json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(p_domain)).get_number('sample_percent');")
(root/'003_policy.sql').write_text(s,encoding='utf-8')
s=old('RRL_STOCK_QC_GATE_PACKAGE_BODY.sql')
s=change(s,"  j.put('warehouse',d.get_number('warehouse'));j.put('customer_order',d.get_number('customer_order_id'));", "  j.put('warehouse',d.get_number('warehouse'));j.put('customer_order',d.get_number('customer_order_id'));\n  declare scoped_policy json_object_t:=json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(p_domain));begin\n   if scoped_policy.has('policy_stamp')then j.put('scope_policy_stamp',scoped_policy.get_string('policy_stamp'));end if;end;")
s=change(s,"  RRL_STOCK_QC_POLICY.settings_for_plan(p_domain,v_mode,v_independent);v_marked", "  RRL_STOCK_QC_POLICY.settings_for_plan(p_domain,v_mode,v_independent);v_marked") if False else s
# Keep assert_approved read-only: write the exemption only at existing execution entrypoints.
a="  if weight_ok and RRL_WH_FINAL_SCALE_ADMISSION.approved(p_domain,v_weight_op)!=1 then weight_ok:=false;end if;"
s=change(s,a,a+"\n  if v_mode in('ANY','WEIGHT','BOTH') and json_object_t.parse(RRL_QC_SCOPE_READ.exemption_json(p_domain)).get_boolean('eligible')then weight_ok:=true;end if;")
s=change(s,"   j.put('unique_mark_control_required',RRL_STOCK_QC_MARK.required_for_plan(domain)=1);", "   j.put('quality_policy',json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(domain)));\n   j.put('weight_exemption',json_object_t.parse(RRL_QC_SCOPE_READ.exemption_json(domain)));\n   j.put('unique_mark_control_required',RRL_STOCK_QC_MARK.required_for_plan(domain)=1);")
(root/'004_gate.sql').write_text(s,encoding='utf-8')
s=old('RRL_STOCK_SHIPPING_CORE_PACKAGE_BODY.sql')
s=change(s,"  if v_kind='SHIP_PALLET' then RRL_STOCK_QC_GATE.assert_approved(p_domain);end if;", "  if v_kind='SHIP_PALLET' then RRL_STOCK_QC_GATE.assert_approved(p_domain);\n   RRL_QC_SCOPE_READ.record_exemption(p_domain,RRL_STOCK_QC_GATE.signature_for_plan(p_domain));end if;")
(root/'005_shipping.sql').write_text(s,encoding='utf-8')
s=old('RRL_STOCK_PALLET_QC_CMD_PACKAGE_BODY.sql')
s=change(s,"   RRL_STOCK_QC_CASE.project(v.to_clob,v_ready,0,1,p_actor,op,null);", "   if v_ready=1 then RRL_QC_SCOPE_READ.record_exemption(v.to_clob,RRL_STOCK_QC_GATE.signature_for_plan(v.to_clob));end if;\n   RRL_STOCK_QC_CASE.project(v.to_clob,v_ready,0,1,p_actor,op,null);")
s=change(s,"  RRL_STOCK_QC_CASE.project(v.to_clob,v_ready,case when passed=0 then 1 else 0 end,0,p_actor,op,v_reason);", "  if v_ready=1 then RRL_QC_SCOPE_READ.record_exemption(v.to_clob,RRL_STOCK_QC_GATE.signature_for_plan(v.to_clob));end if;\n  RRL_STOCK_QC_CASE.project(v.to_clob,v_ready,case when passed=0 then 1 else 0 end,0,p_actor,op,v_reason);")
(root/'006_quality.sql').write_text(s,encoding='utf-8')
p=root/'002_reader.sql';s=p.read_text(encoding='utf-8-sig').replace("if not proof.get_boolean('eligible') then return;end if;", "if not proof.get_boolean('eligible') then return;end if;\n  if proof.get_object('policy').get_string('mode') not in('ANY','WEIGHT','BOTH')then return;end if;");p.write_text(s,encoding='utf-8')
