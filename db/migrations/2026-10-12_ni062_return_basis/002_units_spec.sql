create or replace package RRL_STORE_RETURN_UNIT_CORE authid definer as
 function approved_proof(p_approval varchar2)return clob;
 function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob;
 function disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_basis varchar2)return clob;
 function select_disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob,p_basis varchar2)return clob;
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob);
end;

/
