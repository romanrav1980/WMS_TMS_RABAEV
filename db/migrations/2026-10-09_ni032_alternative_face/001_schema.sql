declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_FACE_ASSIGNMENT' and COLUMN_NAME='UNIT_VOLUME_M3';
 if n=0 then execute immediate 'alter table RRL_PICK_FACE_ASSIGNMENT add (UNIT_VOLUME_M3 number,BASE_UOM varchar2(20))';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' and COLUMN_NAME='RESERVE_REQUEST_JSON';
 if n=0 then execute immediate 'alter table RRL_PICK_WAVE_REPLENISH_TASK add (RESERVE_REQUEST_JSON clob)';end if;
end;
/
