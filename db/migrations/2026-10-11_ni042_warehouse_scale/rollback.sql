declare n number;begin select count(*)into n from RRL_WH_SCALE_CAPTURE;
 if n>0 then raise_application_error(-20886,'WAREHOUSE_SCALE_ARCHIVE_HISTORY_PREVENTS_REMOVAL');end if;
end;
/
drop trigger RRL_WH_SCALE_CAPTURE_GUARD;
drop trigger RRL_WH_SCALE_DEVICE_GUARD;
drop context RRL_WH_SCALE_CTX;
drop package RRL_WH_SCALE_API;
drop table RRL_WH_SCALE_CAPTURE;
drop table RRL_WH_SCALE_DEVICE;
