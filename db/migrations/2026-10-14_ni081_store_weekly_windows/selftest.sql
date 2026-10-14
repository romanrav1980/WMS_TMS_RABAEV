-- Pure native calculator checks. No table mutation or commit. Run after installation.
declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":null,"delivery_window_to":null}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-14 08:30','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='OK' then raise_application_error(-20999,'wait_until_open: '||nvl(err,'OK'));end if;
 if svc!=to_date('2026-10-14 09:00','YYYY-MM-DD HH24:MI')or svc is null then raise_application_error(-20999,'wait_until_open: wrong service');end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":null,"delivery_window_to":null}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-14 11:45','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='OK' then raise_application_error(-20999,'lunch_gap_not_envelope: '||nvl(err,'OK'));end if;
 if svc!=to_date('2026-10-14 13:00','YYYY-MM-DD HH24:MI')or svc is null then raise_application_error(-20999,'lunch_gap_not_envelope: wrong service');end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":null,"delivery_window_to":null}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-14 11:30','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='OK' then raise_application_error(-20999,'exact_end_allowed: '||nvl(err,'OK'));end if;
 if svc!=to_date('2026-10-14 11:30','YYYY-MM-DD HH24:MI')or svc is null then raise_application_error(-20999,'exact_end_allowed: wrong service');end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":null,"delivery_window_to":null}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-15 09:00','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='STORE_CLOSED' then raise_application_error(-20999,'closed_day: '||nvl(err,'OK'));end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":null,"delivery_window_to":null}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-14 17:50','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='STORE_NO_FEASIBLE_INTERVAL' then raise_application_error(-20999,'no_interval_fits: '||nvl(err,'OK'));end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":null,"delivery_window_to":null}],"store_window_profiles":[]}','TEST',to_date('2026-10-14 09:00','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='DELIVERY_WINDOW_UNCONFIGURED' then raise_application_error(-20999,'missing_profile: '||nvl(err,'OK'));end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":"2026-10-14 09:00:00","delivery_window_to":null}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-14 09:00','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='DELIVERY_WINDOW_PARTIAL' then raise_application_error(-20999,'partial_st: '||nvl(err,'OK'));end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":"2026-10-15 10:00:00","delivery_window_to":"2026-10-15 12:00:00"}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-15 09:00','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='OK' then raise_application_error(-20999,'materialized_wins_closed_day: '||nvl(err,'OK'));end if;
 if svc!=to_date('2026-10-15 10:00','YYYY-MM-DD HH24:MI')or svc is null then raise_application_error(-20999,'materialized_wins_closed_day: wrong service');end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":"2026-10-14 12:00:00","delivery_window_to":"2026-10-14 09:00:00"}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-14 09:00','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='DELIVERY_WINDOW_REVERSED_OR_EMPTY' then raise_application_error(-20999,'reversed_st: '||nvl(err,'OK'));end if;
end;
/

declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin
 RRL_STORE_WINDOW_RULES.resolve('{"members":[{"address":"TEST","delivery_window_from":null,"delivery_window_to":null},{"address":"TEST","delivery_window_from":"2026-10-14 14:00:00","delivery_window_to":"2026-10-14 16:00:00"}],"store_window_profiles":[{"address":"TEST","profile_version":1,"mode":"WEEKLY","time_zone":"Europe/Moscow","windows":[{"weekday":3,"from_minute":540,"to_minute":720},{"weekday":3,"from_minute":780,"to_minute":1080}]}]}','TEST',to_date('2026-10-14 11:45','YYYY-MM-DD HH24:MI'),'Europe/Moscow',30,a,z,svc,kind,err);
 if nvl(err,'OK')!='OK' then raise_application_error(-20999,'mixed_member_intersection: '||nvl(err,'OK'));end if;
 if svc!=to_date('2026-10-14 14:00','YYYY-MM-DD HH24:MI')or svc is null then raise_application_error(-20999,'mixed_member_intersection: wrong service');end if;
end;
/
