select name,type,line,text from user_errors where name not like 'BIN$%';
select operation_id,plan_operation_id,revision_no,decision_kind,previous_tt_id,target_tt_id from RRL_INTERWARE_DECISION where PLAN_OPERATION_ID='IW225.PLAN:09f6017c2a'order by revision_no;
select TARGET_TT_ID,RRL_INTERWARE_ROUTING.target_trip(OPERATION_ID) CURRENT_TARGET from RRL_INTERWARE_PLAN where OPERATION_ID='IW225.PLAN:09f6017c2a';
select STATUS from RRL_TT_HU_LOAD_FACT where TT_ID=33551;
