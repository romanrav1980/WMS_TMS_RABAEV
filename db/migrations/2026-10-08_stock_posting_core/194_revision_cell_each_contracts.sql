create or replace package RRL_STOCK_INV_ENTRY authid definer
 accessible by(function RRL_REVIZION_CELL,function RRL_REVIZION_CELL_KOR,function RRL_INV_CREATE_LINE2,function RRL_INV_CREATE_LINE3,function RRL_INV_CREATE_LINE4) as
 function register_line(p_cell varchar2,p_barcode varchar2,p_article_part varchar2,p_qty number,p_document number,
  p_expiry date,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_lot(p_cell varchar2,p_uid varchar2,p_quantity varchar2,p_unit varchar2,p_document number,
  p_actor varchar2,p_operation varchar2,p_reason varchar2) return varchar2;
end;
/
