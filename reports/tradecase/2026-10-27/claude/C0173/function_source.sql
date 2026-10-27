function RRL_TRADE_RECIPIENT_VERSION(p_ware number,p_recipient varchar2,p_bound number)return number is
 -- C-0173: the recipient version an order line bound to version p_bound may use now. The current accepted version itself, or null.
 -- A later version is compatible only when its accepted payload equals the bound version's accepted payload (RRL_TRADE_MESSAGE
 -- history) after removing ONLY topup_enabled and topup_horizon_days. Several accepted records of that version with the same content
 -- (a replay under a new event id) are one snapshot; records with differing content are ambiguous. Missing/ambiguous history: null.
 c_patch constant varchar2(100):='{"topup_enabled":null,"topup_horizon_days":null}';
 v_current number;v_body clob;v_old clob;n number:=0;v_equal number;
begin
 select VERSION_NO,BODY_JSON into v_current,v_body from RRL_TRADE_DOCUMENT
  where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=p_recipient and STATUS='ACCEPTED';
 if v_current=p_bound then return v_current;end if;
 if p_bound is null or v_current<p_bound then return null;end if;
 for m in(select json_query(REQUEST_JSON,'$.payload' returning clob)PAYLOAD from RRL_TRADE_MESSAGE
  where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=p_recipient and VERSION_NO=p_bound
   and json_value(RESULT_JSON,'$.status')='ACCEPTED' order by CREATED_AT fetch first 1 rows only)loop
  v_old:=m.PAYLOAD;
 end loop;
 if v_old is null then return null;end if;
 select count(*)into n from RRL_TRADE_MESSAGE where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=p_recipient and VERSION_NO=p_bound
  and json_value(RESULT_JSON,'$.status')='ACCEPTED'
  and(json_query(REQUEST_JSON,'$.payload' returning clob)is null or not json_equal(json_query(REQUEST_JSON,'$.payload' returning clob),v_old));
 if n<>0 then return null;end if;
 select case when json_equal(json_mergepatch(v_old,c_patch returning clob),json_mergepatch(v_body,c_patch returning clob))then 1 else 0 end into v_equal from dual;
 if v_equal=1 then return v_current;end if;
 return null;
exception when no_data_found then return null;
end;
