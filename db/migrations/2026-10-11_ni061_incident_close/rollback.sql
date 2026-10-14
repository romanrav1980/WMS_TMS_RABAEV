declare n number;begin
 select count(*)into n from RRL_INTERWARE_INCIDENT_CLOSE;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_INCIDENT_CLOSURES');end if;
end;
/
drop trigger RRL_INTERWARE_INCIDENT_CLOSE_G;
drop package RRL_INTERWARE_INCIDENT_API;
-- Keep empty additive table for current read projections; revert API/UI before dropping schema.
