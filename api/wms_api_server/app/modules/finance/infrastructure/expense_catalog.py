from typing import Any
import oracledb
from ..contracts import LogisticsCostError

def set_article(gateway: Any,code: str,name: str,scope: str,included: bool,active: bool,version: int,actor: str) -> dict[str,Any]:
    with gateway.transaction("Version additional cost article") as cur:
        cur.execute("select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'create_tt_price')=1",{"actor":actor})
        if cur.fetchone()[0]!=1:raise LogisticsCostError("EXPENSE_CATALOG_FORBIDDEN","Нет полномочий на статьи затрат",403)
        cur.execute("select NAME,OBJECT_SCOPE,INCLUDED_IN_RATE,ACTIVE_FLAG,VERSION_NO,ACTOR from RRL_LOGISTICS_EXP_ARTICLE where CODE=:code for update",{"code":code});old=cur.fetchone()
        params={"code":code,"name":name,"scope":scope,"included":int(included),"active":int(active),"version":version+1,"actor":actor}
        result={"code":code,"name":name,"scope":scope,"included_in_rate":included,"active":active,"version":version+1}
        if old:
            if old[4]!=version:
                if old==(name,scope,int(included),int(active),version+1,actor):return result
                raise LogisticsCostError("EXPENSE_ARTICLE_VERSION_CONFLICT","Обновите версию статьи")
            cur.execute("update RRL_LOGISTICS_EXP_ARTICLE set NAME=:name,OBJECT_SCOPE=:scope,INCLUDED_IN_RATE=:included,ACTIVE_FLAG=:active,VERSION_NO=:version,ACTOR=:actor,CHANGED_AT=systimestamp where CODE=:code",params)
        else:
            if version!=0:raise LogisticsCostError("EXPENSE_ARTICLE_VERSION_CONFLICT","Статья ещё не создана")
            cur.execute("insert into RRL_LOGISTICS_EXP_ARTICLE(CODE,NAME,OBJECT_SCOPE,INCLUDED_IN_RATE,ACTIVE_FLAG,VERSION_NO,ACTOR)values(:code,:name,:scope,:included,:active,:version,:actor)",params)
        return result
