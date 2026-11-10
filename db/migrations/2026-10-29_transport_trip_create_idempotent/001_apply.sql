-- Идемпотентное создание обычного транспортного рейса (D001.5).
-- Повтор неизменного запроса с тем же operation_id возвращает тот же task_id;
-- изменённый payload даёт конфликт. Повторяет журнальный паттерн RRL_CLUSTER_CREATE_RESULT.

CREATE TABLE RRL_TRIP_CREATE_RESULT (
  OPERATION_ID   VARCHAR2(100) NOT NULL,
  ACTOR          VARCHAR2(50)  NOT NULL,
  REQUEST_HASH   VARCHAR2(64)  NOT NULL,
  REQUEST_JSON   CLOB          NOT NULL,
  TRIP_ID        NUMBER,
  RESULT_JSON    CLOB,
  CREATED_AT     TIMESTAMP(6) WITH TIME ZONE DEFAULT systimestamp NOT NULL,
  CONSTRAINT RRL_TRIP_CREATE_RESULT_PK PRIMARY KEY (OPERATION_ID),
  CONSTRAINT RRL_TRIP_CREATE_REQ_JSON CHECK (REQUEST_JSON IS JSON),
  CONSTRAINT RRL_TRIP_CREATE_RES_JSON CHECK (RESULT_JSON IS JSON)
);

CREATE OR REPLACE PACKAGE RRL_TRANSPORT_IDEMPOTENT_API authid definer AS
  procedure create_trip(p_type varchar2, p_day date, p_actor varchar2, p_operation_id varchar2, p_trip out number);
END;
/

CREATE OR REPLACE PACKAGE BODY RRL_TRANSPORT_IDEMPOTENT_API AS
  procedure create_trip(p_type varchar2, p_day date, p_actor varchar2, p_operation_id varchar2, p_trip out number) IS
    request_text varchar2(4000);
    request_hash varchar2(64);
    saved RRL_TRIP_CREATE_RESULT%rowtype;
  BEGIN
    if p_operation_id is null or lengthb(p_operation_id) > 100 then
      raise_application_error(-20886, 'TRANSPORT_OPERATION_ID_REQUIRED');
    end if;
    request_text := '{"transtype":"' || p_type || '","day":"' || to_char(p_day, 'FXYYYY-MM-DD') || '"}';
    select lower(rawtohex(standard_hash(request_text, 'SHA256'))) into request_hash from dual;
    begin
      insert into RRL_TRIP_CREATE_RESULT(OPERATION_ID, ACTOR, REQUEST_HASH, REQUEST_JSON)
        values (p_operation_id, p_actor, request_hash, request_text);
    exception when dup_val_on_index then
      select * into saved from RRL_TRIP_CREATE_RESULT where OPERATION_ID = p_operation_id;
      if saved.ACTOR != p_actor or saved.REQUEST_HASH != request_hash then
        raise_application_error(-20886, 'TRANSPORT_OPERATION_PAYLOAD_CONFLICT');
      end if;
      if saved.RESULT_JSON is null then
        raise_application_error(-20886, 'TRANSPORT_RESULT_INCOMPLETE');
      end if;
      p_trip := saved.TRIP_ID;
      return;
    end;
    RRL_TRANSPORT_EDIT_API.create_trip(p_type, p_day, p_actor, p_trip);
    update RRL_TRIP_CREATE_RESULT
       set TRIP_ID = p_trip, RESULT_JSON = '{"task_id":' || p_trip || '}'
     where OPERATION_ID = p_operation_id;
  END;
END;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (select '2026-10-29-transport-trip-create-idempotent' MIGRATION_ID from dual) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when matched then update set STATUS='APPLIED', APPLIED_AT=sysdate, APPLIED_BY=user
when not matched then insert(MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
values(s.MIGRATION_ID, 'Idempotent ordinary trip create keyed by operation_id', sysdate, user, 'apply.sql', 'rollback.sql', 'APPLIED');
commit;
