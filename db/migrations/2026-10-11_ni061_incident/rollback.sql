declare n number;begin select count(*)into n from RRL_INTERWARE_DECISION where INCIDENT_KIND is not null;if n>0 then raise_application_error(-20990,'INCIDENT_REPORT_FACTS_EXIST_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_interware_routing.sql
alter table RRL_INTERWARE_DECISION drop constraint RRL_IW_DEC_INCIDENT_CK;
alter table RRL_INTERWARE_DECISION drop(INCIDENT_KIND,INCIDENT_DETAIL,EVIDENCE_REFERENCE);
@@003_recompile.sql
