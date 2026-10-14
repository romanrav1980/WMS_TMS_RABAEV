create or replace package body RRL_STOCK_STORE_RETURN_SAP_CMD as
 procedure describe_binding(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);v_approval varchar2(100):=d.get_object('source').get_string('approval_operation_id');m json_object_t:=d.get_object('metadata');
 approved RRL_STORE_RETURN_APPROVAL%rowtype;v_ware number:=m.get_number('warehouse_id');v_cell varchar2(255):=m.get_string('receive_cell');v_sender varchar2(32767):=m.get_string('sender');v_message varchar2(32767):=m.get_string('message_id');v_document varchar2(32767):=m.get_string('return_document');
 v_raw varchar2(32767):=m.get_string('raw_base64');v_hash varchar2(64):=m.get_string('payload_hash');v_bytes raw(32767);n number;v_xml varchar2(32767);v_quantity_text varchar2(40):=m.get_string('quantity');
 begin
 if RRL_HAS_WRIGHT(p_actor,'sap_return_import')!=1 then raise_application_error(-20882,'SAP_RETURN_IMPORT_FORBIDDEN');end if;
 select * into approved from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=v_approval;
 if m.get_string('receipt_operation_id') is null or m.get_string('receipt_operation_id')!=approved.RECEIPT_OPERATION_ID
 or m.get_number('line_no') is null or m.get_number('line_no')!=approved.LINE_NO
 or m.get_string('article') is null or m.get_string('article')!=approved.ARTICLE
 or m.get_string('lot_uid') is null or m.get_string('lot_uid')!=approved.LOT_UID
 or m.get_string('base_uom') is null or m.get_string('base_uom')!=approved.BASE_UOM
 or nvl(m.get_string('return_basis'),'ACCEPTED')!=approved.RETURN_BASIS
 or m.get_string('disposition') is null or m.get_string('disposition')!=approved.DISPOSITION
 or RRL_STOCK_MATH.quantity(m.get_string('quantity'))!=approved.BASE_QTY then raise_application_error(-20886,'SAP_RETURN_ORIGINAL_APPROVAL_MISMATCH');end if;
 if trim(v_sender) is null or lengthb(v_sender)>100 or trim(v_message) is null or lengthb(v_message)>100 or trim(v_document) is null or lengthb(v_document)>100 then raise_application_error(-20886,'SAP_RETURN_SENDER_MESSAGE_DOCUMENT_REQUIRED');end if;
 if v_ware is null or v_ware!=trunc(v_ware) or v_ware<1 or v_cell is null then raise_application_error(-20886,'SAP_RETURN_WAREHOUSE_RECIPIENT_REQUIRED');end if;
 select count(*) into n from RRL_WARES where ID=v_ware and DEFAULT_RECEIVE_CELL=v_cell;
 if n!=1 then raise_application_error(-20886,'SAP_RETURN_CONFIGURED_RECEIVING_ZONE_REQUIRED');end if;
 select count(*) into n from RRL_CELLS where WARE_ID=v_ware and CELL=v_cell and nvl(BLOCKED_FOR_ACCEPT,0)=0;
 if n!=1 then raise_application_error(-20886,'SAP_RETURN_RECEIVING_ZONE_UNAVAILABLE');end if;
 if v_raw is null or lengthb(v_raw)>21848 or v_hash is null or not regexp_like(v_hash,'^[0-9a-f]{64}$','c') then raise_application_error(-20886,'SAP_RETURN_ORIGINAL_XML_REQUIRED');end if;
 v_bytes:=utl_encode.base64_decode(utl_raw.cast_to_raw(v_raw));
 if length(v_bytes)>16384 or lower(rawtohex(sys.dbms_crypto.hash(v_bytes,sys.dbms_crypto.hash_sh256)))!=v_hash then raise_application_error(-20886,'SAP_RETURN_ORIGINAL_XML_HASH_CONFLICT');end if;
 v_xml:=utl_i18n.raw_to_char(v_bytes,'AL32UTF8');
 if instr(upper(v_xml),'<!DOCTYPE')>0 or instr(upper(v_xml),'<!ENTITY')>0 then raise_application_error(-20886,'SAP_RETURN_XML_DTD_FORBIDDEN');end if;
 select count(*) into n from xmltable('/WarehouseStoreReturn[@version="1" or @version="2"]' passing xmltype(v_xml)
 columns contract_version varchar2(10)path '@version',return_basis varchar2(10)path 'OriginalReceiptDisposition',sender varchar2(100) path 'Sender',message_id varchar2(100) path 'MessageId',return_document varchar2(100) path 'ReturnDocumentNumber',
 approval_id varchar2(100) path 'ApprovalOperationId',receipt_id varchar2(100) path 'OriginalReceiptOperationId',line_no number path 'OriginalLineNumber',
 ware_id number path 'WarehouseId',receive_cell varchar2(255) path 'ReceiveCell',article varchar2(160) path 'Article',lot_uid varchar2(200) path 'LotId',
 qty varchar2(40) path 'Quantity',base_uom varchar2(20) path 'Quantity/@unit',disposition varchar2(20) path 'Disposition') x
 where((x.contract_version='1'and x.return_basis is null and approved.RETURN_BASIS='ACCEPTED')or(x.contract_version='2'and x.return_basis=approved.RETURN_BASIS))
 and x.sender=v_sender and x.message_id=v_message and x.return_document=v_document and x.approval_id=v_approval
 and x.receipt_id=approved.RECEIPT_OPERATION_ID and x.line_no=approved.LINE_NO and x.ware_id=v_ware and x.receive_cell=v_cell
 and x.article=approved.ARTICLE and x.lot_uid=approved.LOT_UID and x.qty=v_quantity_text and x.base_uom=approved.BASE_UOM and x.disposition=approved.DISPOSITION;
 if n!=1 then raise_application_error(-20886,'SAP_RETURN_ORIGINAL_XML_FIELDS_CONFLICT');end if;
 select count(*) into n from RRL_STORE_RETURN_SAP where APPROVAL_OPERATION_ID=v_approval or(SAP_SENDER=v_sender and(RETURN_DOCUMENT=v_document or MESSAGE_ID=v_message));
 if n!=0 then raise_application_error(-20886,'SAP_RETURN_APPROVAL_OR_DOCUMENT_ALREADY_BOUND');end if;
 p_domain:=json_object_t();if approved.RETURN_BASIS!='ACCEPTED'then p_domain.put('return_basis',approved.RETURN_BASIS);end if;p_domain.put('approval_operation_id',v_approval);p_domain.put('sender',v_sender);p_domain.put('message_id',v_message);p_domain.put('return_document',v_document);p_domain.put('warehouse_id',v_ware);p_domain.put('receive_cell',v_cell);p_domain.put('payload_hash',v_hash);
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_binding(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_APPROVAL',v.get_string('approval_operation_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_SAP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','SAP.RETURN.DOC:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(v.get_string('sender')||chr(0)||v.get_string('return_document'),'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');v_approval varchar2(100):=d.get_object('source').get_string('approval_operation_id');
 v_dummy varchar2(100);plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_sender varchar2(100);v_message varchar2(100);v_document varchar2(100);v_ware number;v_cell varchar2(255);v_raw clob;v_hash varchar2(64);
 begin
 select OPERATION_ID into v_dummy from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=v_approval for update;
 describe_binding(p_request,p_actor,fresh);
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'SAP_RETURN_SOURCE_CHANGED');end if;
 v_sender:=v.get_string('sender');v_message:=v.get_string('message_id');v_document:=v.get_string('return_document');v_ware:=v.get_number('warehouse_id');v_cell:=v.get_string('receive_cell');v_raw:=m.get_string('raw_base64');v_hash:=v.get_string('payload_hash');
 insert into RRL_STORE_RETURN_SAP(OPERATION_ID,APPROVAL_OPERATION_ID,SAP_SENDER,MESSAGE_ID,RETURN_DOCUMENT,WARE_ID,RECEIVE_CELL,ORIGINAL_XML_BASE64,ORIGINAL_SHA256,IMPORTED_BY)values(op,v_approval,v_sender,v_message,v_document,v_ware,v_cell,v_raw,v_hash,p_actor);
 if v.has('return_basis')then j.put('return_basis',v.get_string('return_basis'));end if;j.put('operation_id',op);j.put('approval_operation_id',v_approval);j.put('return_document',v_document);j.put('warehouse_id',v_ware);j.put('receive_cell',v_cell);j.put('sap_contract_imported',true);j.put('external_ack_created',false);j.put('warehouse_stock_changed',false);p_result:=j.to_clob;
 end;
end;

/
