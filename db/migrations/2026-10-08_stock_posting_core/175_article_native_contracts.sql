create or replace package ARTICULS_SP_OLD accessible by(package ARTICULS) is
  function ei(articul1 varchar2) return varchar2;
  function UPDATE_MOD(
    ID1             INTEGER,
    ARTICUL1        VARCHAR2,
    NAME1           VARCHAR2,
    SHT_IN_KOR1     NUMBER,
    SHT_WEIGHT1     NUMBER,
    KARTON_WEIGHT1  NUMBER,
    DELETED1        INTEGER,
    SHK_SHT1        VARCHAR2,
    SHK_KOR1        VARCHAR2,
    X               NUMBER,
    Y               NUMBER,
    Z               NUMBER,
    BRT_KOR         NUMBER
  ) return int;
  function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int;
  function eans(art1 varchar2) return varchar2;
end ARTICULS_SP_OLD;

/

create or replace package ARTICULS is
  function ei(articul1 varchar2) return varchar2;
  function UPDATE_MOD(
    ID1             INTEGER,
    ARTICUL1        VARCHAR2,
    NAME1           VARCHAR2,
    SHT_IN_KOR1     NUMBER,
    SHT_WEIGHT1     NUMBER,
    KARTON_WEIGHT1  NUMBER,
    DELETED1        INTEGER,
    SHK_SHT1        VARCHAR2,
    SHK_KOR1        VARCHAR2,
    X               NUMBER,
    Y               NUMBER,
    Z               NUMBER,
    BRT_KOR         NUMBER
  ,p_actor varchar2 default null) return int;
  function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int;
  function eans(art1 varchar2) return varchar2;
end ARTICULS;

/
