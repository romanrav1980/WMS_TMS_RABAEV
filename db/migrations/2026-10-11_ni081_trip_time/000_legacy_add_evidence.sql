FUNCTION        RRL_TRASPORT_TASK_ADD (
    TRANSTYPE1    VARCHAR2 ,
    SHIPMENT_DATE1 DATE , 
    user_id1 varchar2
) return int
IS
ID1 int;
BEGIN

    SELECT RRL_TRANSPORT_TASK_SQ.Nextval INTO ID1 FROM DUAL;

    insert into    RRL_TRANSPORT_TASK
    (
        ID ,
        CREATEDATE , 
        TRANSTYPE ,
        SHIPMENT_DATE
    ) values (
        ID1 ,
        SYSDATE ,
        TRANSTYPE1 ,
        SHIPMENT_DATE1 
    )    ; 
    
    return ID1;

END  RRL_TRASPORT_TASK_ADD ;
