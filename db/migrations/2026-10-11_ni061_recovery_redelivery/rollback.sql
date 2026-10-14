declare n number;begin select count(*)into n from RRL_IW_RECOVERY_ST_BIND;if n>0 then raise_application_error(-20878,'RETAINED_RECOVERY_DELIVERY_REQUIRES_FORWARD_FIX');end if;end;
/
@@000_before_rrl_stock_interware_next_package_body.sql
drop trigger RRL_IW_REC_ST_INSERT_GUARD;
drop trigger RRL_IW_REC_DISPATCH_GUARD;
drop trigger RRL_IW_REC_ST_IMMUTABLE;
drop package RRL_STOCK_IW_RECOVERY_NEXT;
drop table RRL_IW_RECOVERY_DISPATCH;
drop table RRL_IW_RECOVERY_ST_BIND;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
