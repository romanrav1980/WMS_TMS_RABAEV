merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-266-sap-gateway-service-actor'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Least privilege current SAP file gateway actor and explicit source warehouse grant',sysdate,user,
'db/migrations/2026-10-11_sap_gateway_actor/apply.sql','db/migrations/2026-10-11_sap_gateway_actor/rollback.sql','APPLIED',
'Original worker actor absent before266; nowSAP_GATEWAY active/random unexposedsecret/4SAPsource roles/no GUI-receipt-ST rights. Nativebody currentSAPwide scope only; localprivate existingworker raw264sameMessage archivedoneXML-result/source2/P20H20 unchanged. First31char role failed fullDMLrollback, shortroles fitlegacy30. No realSAPnetwork acknowledgment.');
commit;
