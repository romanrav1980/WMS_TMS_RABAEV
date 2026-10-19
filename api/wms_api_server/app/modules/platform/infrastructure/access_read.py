"""Bounded read models protected by the same native scope authority."""
from typing import Any
from .metadata_io import MetadataError, rows, translate, json_object
import oracledb
from .workspace_navigation import read_workspace_navigation

SCOPE_KINDS = ["WAREHOUSE","DC","STORE","REGION","CARRIER","ZONE","ORG_BRANCH","GROUP","SELF","NETWORK","PLATFORM"]

class AccessRead:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def workspaces(self, actor: str, capability: str | None = None) -> dict[str,Any]:
        return read_workspace_navigation(self.gateway, actor, capability)

    def read(self, actor: str, sql: str, params: dict[str,Any] | None = None, permission: str = "access_admin_view") -> list[dict[str,Any]]:
        try:
            with self.gateway.transaction("access.read") as cursor:
                cursor.callproc("RRL_ACCESS_API.assert_allowed",[actor,permission,"PLATFORM",None,None])
                cursor.execute(sql,params or {})
                return rows(cursor)
        except oracledb.DatabaseError as error:
            raise translate(error) from error

    def catalog(self, actor: str) -> dict[str,Any]:
        roles = self.read(actor,"select ROLE_ID,TITLE,ACTIVE,VERSION_NO VERSION from RRL_ACCESS_ROLE order by ROLE_ID fetch first 200 rows only")
        rights = self.read(actor,"select ROLE_ID,PERMISSION from RRL_ACCESS_ROLE_RIGHT order by ROLE_ID,PERMISSION fetch first 40000 rows only")
        for role in roles:
            role["active"] = bool(role["active"])
            role["permissions"] = [r["permission"] for r in rights if r["role_id"] == role["role_id"]]
        legacy = self.read(actor,"select distinct lower(RIGHT1) PERMISSION from RIGHTS where RIGHT1 is not null order by 1 fetch first 1000 rows only")
        return {"roles":roles,"scope_kinds":SCOPE_KINDS,"rights":sorted({r["permission"] for r in rights+legacy}|{"access_admin_view","access_role_manage","access_group_manage","access_assign_manage","knowledge_edit","knowledge_publish","knowledge_admin","expense_logist_approve","expense_finance_approve"})}

    def groups(self, actor: str, query: str, limit: int) -> list[dict[str,Any]]:
        data = self.read(actor,"""select GROUP_ID,TITLE,MEMBER_KIND,VERSION_NO VERSION,ACTIVE from RRL_ACCESS_GROUP
          where instr(lower(TITLE),lower(:query))>0 or instr(lower(GROUP_ID),lower(:query))>0 or :query is null order by GROUP_ID fetch first :lim rows only""",{"query":query,"lim":limit})
        for item in data: item["active"] = bool(item["active"])
        return data

    def group(self, actor: str, group_id: str) -> dict[str,Any]:
        data = self.read(actor,"select GROUP_ID,TITLE,MEMBER_KIND,VERSION_NO VERSION,ACTIVE from RRL_ACCESS_GROUP where GROUP_ID=:id",{"id":group_id})
        if not data: raise MetadataError("GROUP_NOT_FOUND",404)
        data[0]["active"] = bool(data[0]["active"])
        data[0]["members"] = self.read(actor,"""select m.KIND,m.OBJECT_ID,o.TITLE from RRL_ACCESS_GROUP_MEMBER m join RRL_ACCESS_GROUP g on g.GROUP_ID=m.GROUP_ID and g.VERSION_NO=m.VERSION_NO
         join RRL_ACCESS_OBJECT o on o.KIND=m.KIND and o.OBJECT_ID=m.OBJECT_ID where g.GROUP_ID=:id order by m.KIND,m.OBJECT_ID""",{"id":group_id})
        return data[0]

    def preview_group(self, actor: str, payload: dict[str,Any]) -> dict[str,Any]:
        group_id = payload["group_id"]
        data = self.read(actor,"select VERSION_NO VERSION,ACTIVE from RRL_ACCESS_GROUP where GROUP_ID=:id",{"id":group_id})
        version = data[0]["version"] if data else 0
        if version != payload["expected_version"]: raise MetadataError("VERSION_CONFLICT",409)
        current = self.read(actor,"select KIND,OBJECT_ID from RRL_ACCESS_GROUP_MEMBER where GROUP_ID=:id and VERSION_NO=:version",{"id":group_id,"version":version})
        before = {(item["kind"],item["object_id"]) for item in current}
        after = {(item["kind"],item["object_id"]) for item in payload["members"]}
        affected = self.read(actor,"""select ASSIGNMENT_ID,USERNAME,ROLE_ID,MEMBERSHIP,count(*)over() TOTAL_MATCHES
         from RRL_ACCESS_ASSIGNMENT where SCOPE_KIND='GROUP' and SCOPE_ID=:id and REVOKED_AT is null
         and(VALID_UNTIL is null or VALID_UNTIL>systimestamp) order by ASSIGNMENT_ID fetch first 200 rows only""",{"id":group_id})
        return {"group_id":group_id,"version":version,"added":[{"kind":k,"object_id":i} for k,i in sorted(after-before)],
                "removed":[{"kind":k,"object_id":i} for k,i in sorted(before-after)],"affected_assignments":affected,
                "affected_total":affected[0]["total_matches"] if affected else 0,"preview_limit":200,
                "activation_changed":bool(data and bool(data[0]["active"])!=payload["active"]),
                "snapshot_note":"Snapshot membership stays fixed; activation changes can affect it."}

    def objects(self, actor: str, kind: str, query: str, limit: int) -> list[dict[str,Any]]:
        data = self.read(actor,"""select KIND,OBJECT_ID,TITLE,PARENT_KIND,PARENT_ID,VERSION_NO VERSION,ACTIVE from RRL_ACCESS_OBJECT
         where KIND=:kind and(instr(lower(TITLE),lower(:query))>0 or instr(lower(OBJECT_ID),lower(:query))>0 or :query is null) order by OBJECT_ID fetch first :lim rows only""",{"kind":kind,"query":query,"lim":limit})
        for item in data: item["active"] = bool(item["active"])
        return data

    def assignments(self, actor: str, username: str | None, limit: int, own: bool = False) -> list[dict[str,Any]]:
        sql = """select ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,SNAPSHOT_VERSION,
         to_char(VALID_FROM at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') VALID_FROM,
         to_char(VALID_UNTIL at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') VALID_UNTIL,
         to_char(REVOKED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') REVOKED_AT,ASSIGNED_BY,REASON,VERSION_NO VERSION,
         case when REVOKED_AT is not null then 'REVOKED' when VALID_FROM>systimestamp then 'SCHEDULED'
          when VALID_UNTIL is not null and VALID_UNTIL<=systimestamp then 'EXPIRED' else 'ACTIVE' end ASSIGNMENT_STATE
         from RRL_ACCESS_ASSIGNMENT
         where(:username is null or lower(trim(USERNAME))=lower(trim(:username))) order by ASSIGNMENT_ID fetch first :lim rows only"""
        if own:
            return self.gateway.fetch_all(sql,{"username":actor,"lim":limit})
        return self.read(actor,sql,{"username":username,"lim":limit})

    def navigation(self, actor: str) -> dict[str,Any]:
        data = self.gateway.fetch_all("""select REVISION ACCESS_REVISION,
         RRL_ACCESS_API.allowed(:actor,'access_admin_view','PLATFORM',null) ACCESS_ADMIN,
         RRL_ACCESS_API.allowed(:actor,'knowledge_edit','PLATFORM',null) KNOWLEDGE_EDITOR,
         RRL_ACCESS_API.allowed(:actor,'knowledge_publish','PLATFORM',null) KNOWLEDGE_PUBLISH,
         RRL_ACCESS_API.allowed(:actor,'access_role_manage','PLATFORM',null) MANAGE_ROLES,
         RRL_ACCESS_API.is_admin(:actor) MANAGE_OBJECTS,
         RRL_ACCESS_API.allowed(:actor,'access_group_manage','PLATFORM',null) MANAGE_GROUPS,
         RRL_ACCESS_API.allowed(:actor,'access_assign_manage','PLATFORM',null) MANAGE_ASSIGNMENTS
         from RRL_ACCESS_REV where ID=1""",{"actor":actor})[0]
        return {**{key:bool(value) for key,value in data.items() if key!="access_revision"},"access_revision":data["access_revision"],"username":actor}

    def me(self, actor: str, legacy_group: str) -> dict[str,Any]:
        capabilities = self.navigation(actor)
        return {"username":actor,"legacy_group":legacy_group,"assignments":self.assignments(actor,actor,100,True),"access_revision":capabilities["access_revision"],"capabilities":capabilities}

    def explain(self, actor: str, target: str, permission: str, kind: str, object_id: str | None) -> dict[str,Any]:
        if actor != target: self.read(actor,"select 1 from dual")
        data = self.gateway.fetch_all("select RRL_ACCESS_API.explanation(:actor,:permission,:kind,:id) EXPLANATION from dual",
                                     {"actor":target,"permission":permission,"kind":kind,"id":object_id})[0]
        return json_object(data["explanation"])
