package RRL_STOCK_ELIGIBILITY authid definer as
 function reason(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number default 0,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null) return varchar2;
 procedure assert_source(p_uid varchar2,p_cell varchar2,p_warehouse number,p_quantity number,
  p_min_days number default null,p_min_percent number default null,p_purpose varchar2 default 'ALLOCATE',
  p_owner_reservation number default null,p_article varchar2 default null);
end;