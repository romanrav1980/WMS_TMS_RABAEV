create or replace package RRL_ASM_META_SCOPE authid definer
 accessible by (package RRL_ASSEMBLY_SCALE_API) as
 procedure begin_change(p_task number,p_actor nvarchar2);
end;
/
