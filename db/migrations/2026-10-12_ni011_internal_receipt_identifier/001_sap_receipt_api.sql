create or replace package body RRL_SAP_RECEIPT_API as

 g_allowed boolean:=false;

 function pallet_write_allowed return boolean is begin return g_allowed; end;

 procedure register_pallet(p_sscc varchar2,p_articul varchar2,p_expiry date,p_produced date,

 p_qty number,p_naklad number,p_actor varchar2) is n number;v_reg_sscc varchar2(32);v_sum number:=0;

 begin

 select count(*) into n from RRL_SAP_SUPPLY_ORDER where NAKLAD_ID=p_naklad;

 if n!=1 or p_qty<=0 then raise_application_error(-20803,'Invalid SAP receiving document/quantity'); end if;

 if p_sscc is null or length(p_sscc)>50 or lengthb(p_sscc)>150 or regexp_like(p_sscc,'[[:space:][:cntrl:]]')then raise_application_error(-20803,'Invalid physical pallet identifier');end if;
 if regexp_like(p_sscc,'^[0-9]{18}$')then
  for i in 1..17 loop v_sum:=v_sum+to_number(substr(p_sscc,i,1))*case when mod(i,2)=1 then 3 else 1 end;end loop;
  if mod(10-mod(v_sum,10),10)=to_number(substr(p_sscc,18,1))then v_reg_sscc:=p_sscc;end if;
 end if;
 g_allowed:=true;

 begin

 insert into RRL_PALLETS(UID_PALLET,SSCC,ARTICUL,CREATION_DATE,EXPIRY_DATE,PRODUCED_DATE,UNIT_COUNT,PRIHOD_NAKLAD_ID,KLADOVSHIK,PRINTED)

 values(p_sscc,v_reg_sscc,p_articul,sysdate,p_expiry,p_produced,p_qty,p_naklad,substr(p_actor,1,15),0);

 g_allowed:=false;

 exception when others then g_allowed:=false; raise;

 end;

 end;

end;


/
