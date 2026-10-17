-- PREPARED ONLY. Root review/apply required; no API/capture/QC consumer.
create or replace package RRL_SHIPPING_GROSS_READ authid definer as
 procedure freeze(p_source clob,p_actor nvarchar2,p_result out clob);
end;
/
