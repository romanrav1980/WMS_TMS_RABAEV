create or replace FUNCTION        RRL_HAS_WRIGHT( user_id varchar2 , wright_name varchar2 )
    RETURN int IS 
    tmpVar varchar2(255);
    
BEGIN

begin

--return 1;
select id into tmpVar from rusers where id=user_id and USER_GROUP='GLOBAL_ADMIN';
return 1;

exception
 WHEN NO_DATA_FOUND THEN
    null;
end;

    select  RUSERS.USER_GROUP into tmpVar from RUSERS , RABAEV.RIGHTS where 
            RUSERS.ID=user_id and RIGHTS.USER_GROUP=RUSERS.USER_GROUP and RIGHT1= wright_name ;

   
    RETURN 1;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 0;
END RRL_HAS_WRIGHT;

/
