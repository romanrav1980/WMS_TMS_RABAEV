declare n number;begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_PALLETS_HUCELL_I1';
 if n=0 then execute immediate q'~create index RRL_PALLETS_HUCELL_I1 on RRL_PALLETS(case when HU_KIND='CONTAINER' then HU_CURRENT_CELL end)~';end if;
end;
/
