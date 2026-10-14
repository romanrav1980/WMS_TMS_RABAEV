declare n number;begin select count(*)into n from RRL_PICK_WEIGHT_CHOICE;if n>0 then raise_application_error(-20863,'WEIGHT_CHOICE_RETAIN_ARCHIVE_FORWARD_REPAIR');end if;end;
/
@@000_before_reader.sql
drop trigger RRL_WEIGHT_CHOICE_GUARD;
drop context RRL_WEIGHT_CHOICE_CTX;
drop package RRL_WEIGHT_BOX_CHOICE_API;
drop table RRL_PICK_WEIGHT_CHOICE;
