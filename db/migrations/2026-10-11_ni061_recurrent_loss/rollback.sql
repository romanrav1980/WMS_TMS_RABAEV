declare n number;begin
 select count(*)into n from(select PHYSICAL_UNIT_KEY from RRL_INTERWARE_SHORTAGE_UNIT group by PHYSICAL_UNIT_KEY having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_RECURRENT_LOSS_CANNOT_ROLL_BACK_SINGLE_KEY');end if;
 select count(*)into n from(select PHYSICAL_UNIT_KEY from RRL_INTERWARE_RECOVERY_UNIT group by PHYSICAL_UNIT_KEY having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_RECURRENT_RECOVERY_CANNOT_ROLL_BACK_SINGLE_KEY');end if;
end;
/
@@000_before_rrl_stock_interware_short_cmd_package_body.sql
@@../2026-10-11_ni061_shortage_disposition/003_guards.sql
alter table RRL_INTERWARE_SHORTAGE_UNIT drop primary key;
alter table RRL_INTERWARE_SHORTAGE_UNIT add constraint RRL_IW_LOSS_SINGLE_UNIT_PK primary key(PHYSICAL_UNIT_KEY);
alter table RRL_INTERWARE_RECOVERY_UNIT drop primary key;
alter table RRL_INTERWARE_RECOVERY_UNIT add constraint RRL_IW_REC_SINGLE_UNIT_PK primary key(PHYSICAL_UNIT_KEY);
@@../2026-10-08_stock_posting_core/014b_recompile.sql
