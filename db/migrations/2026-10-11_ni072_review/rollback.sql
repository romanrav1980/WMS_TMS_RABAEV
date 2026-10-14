declare n number;begin
 select count(*)into n from RRL_DAY_REVIEW;
 if n>0 then raise_application_error(-20886,'DAY_REVIEW_HISTORY_RETAINED');end if;
end;
/
drop trigger RRL_DAY_REVIEW_GUARD;
drop package RRL_DAY_REVIEW_API;
drop table RRL_DAY_REVIEW;
