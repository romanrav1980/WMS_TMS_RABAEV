merge into RIGHTS r using(select 'GLOBAL_ADMIN'USER_GROUP,'warehouse_day_inspect'RIGHT1 from dual)s
on(r.USER_GROUP=s.USER_GROUP and upper(r.RIGHT1)=upper(s.RIGHT1))
when not matched then insert(RIGHT1,USER_GROUP,ID,DESCR)
values(s.RIGHT1,s.USER_GROUP,(select nvl(max(ID),0)+1 from RIGHTS),'Подтверждение осмотра грузовой зоны начальником склада');
/
