select name,type,line,text from user_errors where name not like 'BIN$%';
select TT_ID,STATUS,count(*)PLACES,sum(GROSS_WEIGHT_KG)MASS_KG from RRL_TT_HU_LOAD_FACT where TT_ID=33558 group by TT_ID,STATUS;
select MAX_WEIGHT_KG,PALLETS from RRL_TR_VEHICLE where NUM='QC241ede877f6d1';
select ID,TRANSTASK_ID,CONDITION from RRL_SBORKA_PALLETS where ID in(641383,641384);
