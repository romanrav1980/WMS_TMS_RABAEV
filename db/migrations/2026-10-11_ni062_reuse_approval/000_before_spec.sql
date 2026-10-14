CREATE OR REPLACE EDITIONABLE PACKAGE "RABAEV"."RRL_STOCK_RETURN_REUSE" authid definer accessible by(package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_STORE_RETURN_PUT) as
 procedure describe_boxes(p_approval RRL_STORE_RETURN_APPROVAL%rowtype,p_metadata json_object_t,p_scan_uom varchar2,p_batch_source varchar2,p_ware number,p_proof out json_object_t);
 procedure persist_boxes(p_operation varchar2,p_actor varchar2,p_proof json_object_t);
 procedure assert_pick_target(p_receipt RRL_STORE_RETURN_RECEIPT%rowtype,p_target varchar2);
end;
/
