prompt Fix invalid ADD_SFERA_EAN objects against restored legacy SFERA_EAN column name
create or replace procedure RABAEV.ADD_SFERA_EAN (
    row_uid out number,
    TMC_UID in varchar2,
    EAN_SHT varchar2,
    EAN_BL varchar2,
    EAN_KOR varchar2,
    MANUALENTER char,
    SHT_IN_BL integer,
    BL_IN_KOR integer,
    NAME varchar2
)
as
    legacy_uid_column varchar2(64) := '"' || unistr('\FFFD\FFFD\FFFD') || '"';
begin
    execute immediate
        'insert into RABAEV.SFERA_EAN (' ||
        legacy_uid_column ||
        ', TMC_UID, EAN_SHT, EAN_BL, EAN_KOR, MANUALENTER, SHT_IN_BL, BL_IN_KOR, NAME) ' ||
        'values (RABAEV.SFERA_EAN_ID.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8)'
        using TMC_UID, EAN_SHT, EAN_BL, EAN_KOR, MANUALENTER, SHT_IN_BL, BL_IN_KOR, NAME;

    select RABAEV.SFERA_EAN_ID.CURRVAL into row_uid from dual;
end ADD_SFERA_EAN;
/

create or replace function RABAEV.ADD_SFERA_EAN2 (
    TMC_UID in varchar2,
    EAN_SHT varchar2,
    EAN_BL varchar2,
    EAN_KOR varchar2,
    MANUALENTER char,
    SHT_IN_BL integer,
    BL_IN_KOR integer,
    NAME varchar2
) return int
is
    row_uid int;
    legacy_uid_column varchar2(64) := '"' || unistr('\FFFD\FFFD\FFFD') || '"';
begin
    execute immediate
        'insert into RABAEV.SFERA_EAN (' ||
        legacy_uid_column ||
        ', TMC_UID, EAN_SHT, EAN_BL, EAN_KOR, MANUALENTER, SHT_IN_BL, BL_IN_KOR, NAME) ' ||
        'values (RABAEV.SFERA_EAN_ID.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8)'
        using TMC_UID, EAN_SHT, EAN_BL, EAN_KOR, MANUALENTER, SHT_IN_BL, BL_IN_KOR, NAME;

    select RABAEV.SFERA_EAN_ID.CURRVAL into row_uid from dual;
    return row_uid;
end ADD_SFERA_EAN2;
/

begin
  dbms_utility.compile_schema(schema => 'RABAEV', compile_all => false);
end;
/
