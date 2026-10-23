create or replace package RRL_TRADE_TOPUP_READ authid definer as
 -- Identity of everything a proposal's capacity depends on: trip/order versions, vehicle profile and the other
 -- confirmed top-ups of the same trip. A different value means the free space was recalculated by someone else.
 function trip_basis(p_ware number,p_trip varchar2,p_exclude number default null)return varchar2;
 function loading_started(p_ware number,p_trip varchar2)return number;
 function need_confirmed_boxes(p_ware number,p_need varchar2,p_exclude number default null)return number;
 -- Unallocated base quantity of open main trade order lines with the same goods terms; a top-up never takes it.
 function protected_units(p_ware number,p_sku varchar2,p_owner varchar2,p_mrc number)return number;
 -- Eligible free physical units (EA) ordered FEFO: JSON array of {uid,cell,units:[keys...]}; whole boxes (p_step units) per source, up to p_limit units.
 function candidates(p_ware number,p_article varchar2,p_sku varchar2,p_owner varchar2,p_mrc number,p_min_expiry date,p_limit number,p_step number)return clob;
 -- Physical eligibility uses REPLENISH because there is no picking order yet; proposal terms and owner rights are checked separately.
 -- Same eligibility, total whole-box units only (first 200 sources); used to keep protected main demand untouched.
 function eligible_units(p_ware number,p_article varchar2,p_sku varchar2,p_owner varchar2,p_mrc number,p_min_expiry date,p_step number)return number;
 function card(p_id number)return clob;
end;
/
