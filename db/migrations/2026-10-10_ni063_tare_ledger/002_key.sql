create or replace function RRL_TARE_BALANCE_KEY(p_owner number,p_type number,p_condition varchar2,p_kind varchar2,p_id varchar2) return raw authid definer is
 a json_array_t:=json_array_t();
begin a.append(p_owner);a.append(p_type);a.append(p_condition);a.append(p_kind);a.append(p_id);
 return sys.dbms_crypto.hash(utl_i18n.string_to_raw(a.to_string,'AL32UTF8'),sys.dbms_crypto.hash_sh256);
end;
/
