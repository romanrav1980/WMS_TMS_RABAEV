package RRL_TRADE_DOCUMENT_API authid definer as
 procedure configure(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob);
 procedure receive_document(p_ware number,p_actor nvarchar2,p_json clob,p_result out clob);
 procedure retry_document(p_ware number,p_actor nvarchar2,p_event varchar2,p_result out clob);
 procedure read_documents(p_ware number,p_actor nvarchar2,p_mode varchar2,p_kind varchar2,p_key varchar2,p_limit number,p_result out clob);
end;