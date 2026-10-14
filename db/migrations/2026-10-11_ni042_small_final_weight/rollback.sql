declare n number;begin select count(*)into n from RRL_PALLET_TYPE where FINAL_WEIGHT_REQUIRED=1;if n>0 then raise_application_error(-20863,'SMALL_TYPE_POLICY_USED_FORWARD_REPAIR');end if;end;
/
@@000_before_gate.sql
@@000_before_policy.sql
drop trigger RRL_PALLET_TYPE_FINAL_GUARD;
drop context RRL_PALLET_TYPE_CTX;
drop package RRL_PALLET_TYPE_API;
alter table RRL_PALLET_TYPE drop column FINAL_WEIGHT_REQUIRED;
alter table RRL_PALLET_TYPE drop column TYPE_VERSION;
