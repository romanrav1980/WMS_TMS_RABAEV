package body RRL_OUTGOING_QC_ACCESS as
 procedure assert_identifier(p_identifier varchar2,p_actor varchar2)is
  ware number;user_ware number;grp varchar2(100);
 begin
  if p_actor is null or(RRL_HAS_WRIGHT(p_actor,'outgoing_pallet_check')!=1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1
   and RRL_HAS_WRIGHT(p_actor,'CLOSE_OTHOD_NAKLAD')!=1)then raise_application_error(-20882,'OUTGOING_QC_PERMISSION_REQUIRED');end if;
  select WARE_ID into ware from RRL_SBORKA_PALLETS where PALLET_UID=p_identifier;
  select WARE_ID,USER_GROUP into user_ware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if ware is null or(upper(trim(grp))!='GLOBAL_ADMIN'and(user_ware is null or user_ware!=ware))
   then raise_application_error(-20882,'OUTGOING_QC_CURRENT_WARE_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20882,'OUTGOING_QC_CURRENT_SOURCE_AND_ACTOR_REQUIRED');
 end;
end;
