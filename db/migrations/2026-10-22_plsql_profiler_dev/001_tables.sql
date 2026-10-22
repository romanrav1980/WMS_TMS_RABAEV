create table PLSQL_PROFILER_RUNS(
 runid number primary key,related_run number,run_owner varchar2(128),run_date date,
 run_comment varchar2(2047),run_total_time number,run_system_info varchar2(2047),
 run_comment1 varchar2(2047),spare1 varchar2(256));
create table PLSQL_PROFILER_UNITS(
 runid number references PLSQL_PROFILER_RUNS(runid),unit_number number,unit_type varchar2(128),
 unit_owner varchar2(128),unit_name varchar2(128),unit_timestamp date,total_time number,
 spare1 number,spare2 number,primary key(runid,unit_number));
create table PLSQL_PROFILER_DATA(
 runid number,unit_number number,line# number not null,total_occur number,total_time number,
 min_time number,max_time number,spare1 number,spare2 number,spare3 number,spare4 number,
 primary key(runid,unit_number,line#),foreign key(runid,unit_number)references PLSQL_PROFILER_UNITS(runid,unit_number));
create sequence PLSQL_PROFILER_RUNNUMBER start with 1 increment by 1 nocycle;
