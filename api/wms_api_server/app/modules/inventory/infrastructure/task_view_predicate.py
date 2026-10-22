"""Fixed native read predicate shared by queue and exact detail."""
def task_view_predicate() -> str:
    return """(FROM_WARE_ID is not null or TO_WARE_ID is not null)
        and ((select RRL_ACCESS_API.is_admin(:view_actor)from dual)=1 or (
        (FROM_WARE_ID is null or RRL_ACCESS_API.allowed(:view_actor,'warehouse_task_view','WAREHOUSE',to_char(FROM_WARE_ID),ASSIGNED_TO)=1)
        and (TO_WARE_ID is null or RRL_ACCESS_API.allowed(:view_actor,'warehouse_task_view','WAREHOUSE',to_char(TO_WARE_ID),ASSIGNED_TO)=1)))"""


