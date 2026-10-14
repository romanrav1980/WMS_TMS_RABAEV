declare n number;begin select count(*)into n from RRL_LOGISTICS_EXP_ALLOCATION;if n>0 then raise_application_error(-20808,'LOGISTICS_ALLOCATION_FORWARD_CORRECTION_REQUIRED');end if;execute immediate 'drop table RRL_LOGISTICS_EXP_ALLOC_LINE';execute immediate 'drop table RRL_LOGISTICS_EXP_ALLOCATION';end;
/
