-- Additive metadata only; existing historical dimensions remain unknown.
declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_VEHICLE_PROFILE_HIST'and COLUMN_NAME='OUTER_HEIGHT_MM';
 if n=0 then execute immediate 'alter table RRL_VEHICLE_PROFILE_HIST add(OUTER_HEIGHT_MM number(7))';end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_VEHICLE_PROFILE_HIST'and COLUMN_NAME='OUTER_LENGTH_MM';
 if n=0 then execute immediate 'alter table RRL_VEHICLE_PROFILE_HIST add(OUTER_LENGTH_MM number(7))';end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_VEH_OUTER_HEIGHT_CK';
 if n=0 then execute immediate 'alter table RRL_VEHICLE_PROFILE_HIST add constraint RRL_VEH_OUTER_HEIGHT_CK check(OUTER_HEIGHT_MM is null or (OUTER_HEIGHT_MM between 1 and 1000000 and OUTER_HEIGHT_MM>=CARGO_HEIGHT_MM))';end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_VEH_OUTER_LENGTH_CK';
 if n=0 then execute immediate 'alter table RRL_VEHICLE_PROFILE_HIST add constraint RRL_VEH_OUTER_LENGTH_CK check(OUTER_LENGTH_MM is null or (OUTER_LENGTH_MM between 1 and 1000000 and OUTER_LENGTH_MM>=CARGO_LENGTH_MM))';end if;
end;
/
