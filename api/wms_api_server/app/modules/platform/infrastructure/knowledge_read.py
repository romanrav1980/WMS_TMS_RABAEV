"""Native-filtered knowledge revisions; drafts never replace reader publication."""
import json
from typing import Any
from .metadata_io import MetadataError, json_object

SELECT_REV = """select a.ARTICLE_ID,json_value(r.PAYLOAD_JSON,'$.space_id' returning varchar2(80)) SPACE_ID,r.VERSION_NO VERSION,r.STATE STATUS,r.PAYLOAD_JSON,
 r.ACTOR UPDATED_BY,to_char(r.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') UPDATED_AT from RRL_KNOWLEDGE_ARTICLE a
 join RRL_KNOWLEDGE_REV r on r.ARTICLE_ID=a.ARTICLE_ID and r.VERSION_NO={version}
 where RRL_KNOWLEDGE_API.can_read(:actor,r.PAYLOAD_JSON)=1"""
EDITOR = "RRL_ACCESS_API.allowed(:actor,'knowledge_edit','PLATFORM',null)=1"

class KnowledgeRead:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def editor(self, actor: str) -> bool:
        return bool(self.gateway.fetch_all("select RRL_ACCESS_API.allowed(:actor,'knowledge_edit','PLATFORM',null) ALLOWED from dual",{"actor":actor})[0]["allowed"])

    def spaces(self, actor: str) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("""select s.SPACE_ID,s.TITLE,s.VERSION_NO VERSION from RRL_KNOWLEDGE_SPACE s
         where RRL_ACCESS_API.allowed(:actor,'knowledge_edit','PLATFORM',null)=1 or exists(
          select 1 from RRL_KNOWLEDGE_ARTICLE a join RRL_KNOWLEDGE_REV r on r.ARTICLE_ID=a.ARTICLE_ID and r.VERSION_NO=a.PUBLISHED_VERSION
          where json_value(r.PAYLOAD_JSON,'$.space_id' returning varchar2(80))=s.SPACE_ID and a.ARCHIVED=0 and RRL_KNOWLEDGE_API.can_read(:actor,r.PAYLOAD_JSON)=1)
         order by s.SPACE_ID fetch first 200 rows only""",{"actor":actor})

    def articles(self, actor: str, space_id: str | None, query: str, status: str | None, limit: int, published: bool = False) -> list[dict[str,Any]]:
        version = "a.PUBLISHED_VERSION" if published else "case when "+EDITOR+" then a.CURRENT_VERSION else a.PUBLISHED_VERSION end"
        sql = SELECT_REV.format(version=version)
        if published: sql += " and a.ARCHIVED=0"
        sql += " and(:space is null or json_value(r.PAYLOAD_JSON,'$.space_id' returning varchar2(80))=:space) and(:state is null or r.STATE=:state)"
        params = {"actor":actor,"space":space_id,"state":status,"lim":limit}
        for index,word in enumerate(query.casefold().split()[:20]):
            sql += " and instr(lower(r.PAYLOAD_JSON),:word"+str(index)+")>0"
            params["word"+str(index)] = word
        sql += " order by a.ARTICLE_ID fetch first :lim rows only"
        data = self.gateway.fetch_all(sql,params)
        return [self._summary(row) for row in data]

    def _summary(self, row: dict[str,Any]) -> dict[str,Any]:
        payload = json_object(row["payload_json"])
        return {**{k:v for k,v in row.items() if k!="payload_json"},"title":payload["title"],"summary":payload["summary"]}

    def article(self, actor: str, article_id: str, published: bool = False) -> dict[str,Any]:
        version = "a.PUBLISHED_VERSION" if published else "case when "+EDITOR+" then a.CURRENT_VERSION else a.PUBLISHED_VERSION end"
        data = self.gateway.fetch_all(SELECT_REV.format(version=version)+" and a.ARTICLE_ID=:id"+(" and a.ARCHIVED=0" if published else ""),{"actor":actor,"id":article_id})
        if not data: raise MetadataError("ARTICLE_NOT_VISIBLE",404)
        row = data[0]
        return {**json_object(row.pop("payload_json")),**row}

    def history(self, actor: str, article_id: str, limit: int) -> list[dict[str,Any]]:
        if not self.editor(actor): raise MetadataError("ACCESS_DENIED",403)
        self.article(actor,article_id)
        return self.gateway.fetch_all("""select VERSION_NO VERSION,STATE STATUS,ACTOR,to_char(CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') CREATED_AT,REASON from RRL_KNOWLEDGE_REV
         where ARTICLE_ID=:id and RRL_KNOWLEDGE_API.can_read(:actor,PAYLOAD_JSON)=1 order by VERSION_NO desc fetch first :lim rows only""",{"actor":actor,"id":article_id,"lim":limit})

class NativePublishedHelp:
    def __init__(self, reader: KnowledgeRead, actor: str) -> None:
        self.reader = reader
        self.actor = actor
    def search(self, query: str, permissions: set[str], limit: int) -> list[dict[str,str]]:
        return [{k:row[k] for k in ("article_id","title","summary")} for row in self.reader.articles(self.actor,None,query,"PUBLISHED",limit,True)]
    def detail(self, article_id: str, permissions: set[str]) -> dict[str,Any] | None:
        try: row = self.reader.article(self.actor,article_id,True)
        except MetadataError as error:
            if error.status == 404: return None
            raise
        related = row.get("related",[])
        links = []
        if related:
            sql = """select a.ARTICLE_ID,json_value(r.PAYLOAD_JSON,'$.title' returning varchar2(1000)) TITLE from RRL_KNOWLEDGE_ARTICLE a
             join RRL_KNOWLEDGE_REV r on r.ARTICLE_ID=a.ARTICLE_ID and r.VERSION_NO=a.PUBLISHED_VERSION
             join json_table(:ids,'$[*]' columns(ARTICLE_ID varchar2(80) path '$')) j on j.ARTICLE_ID=a.ARTICLE_ID
             where a.ARCHIVED=0 and RRL_KNOWLEDGE_API.can_read(:actor,r.PAYLOAD_JSON)=1 order by a.ARTICLE_ID"""
            links = self.reader.gateway.fetch_all(sql,{"actor":self.actor,"ids":json.dumps(related)})
        return {**row,"revision":str(row["version"]),"related":links}
