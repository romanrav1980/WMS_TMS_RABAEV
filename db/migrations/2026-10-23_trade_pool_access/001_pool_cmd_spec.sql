create or replace package RRL_STOCK_POOL_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_WAVE_LAUNCH_CMD) as
 procedure compile_wave_pool(p_ware number,p_wave number,p_resources in out nocopy json_array_t,p_pools out json_array_t);
 procedure consume_wave_pool(p_pools json_array_t,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 -- C-0162: today's rights for a pool command, called by the runner before the committed-replay branch: the warehouse right
 -- (RRL_ACCESS_API: GLOBAL_ADMIN, legacy group of that warehouse, current scoped assignment) and, for a recorded trade plan, operate
 -- on the owner of every class it promised. A stored receipt is never shown to someone who could not issue the command now.
 procedure assert_access(p_request clob,p_actor varchar2);
end;
/
