"""Explicit read-only connection boundary; no API route and no native write owner."""
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any
from ..contracts_shipping_gross import ShippingGrossReadInput,FrozenShippingGrossRead,parse_shipping_gross_read
from ..domain.models import HuMassError,identity


class ShippingGrossNativeRead:
    def __init__(self,connection_factory:Callable[[],AbstractContextManager[Any]])->None:
        self.connection_factory=connection_factory

    def freeze(self,request:ShippingGrossReadInput,server_actor:str)->FrozenShippingGrossRead:
        import oracledb
        identity(server_actor)
        with self.connection_factory()as connection:
            connection.call_timeout=5000
            cursor=connection.cursor()
            try:
                current=cursor.callfunc('DBMS_TRANSACTION.LOCAL_TRANSACTION_ID',str,[False])
            except BaseException:
                cursor.close()
                raise
            if current is not None:
                cursor.close()
                raise HuMassError('SHIPPING_GROSS_CLEAN_CONNECTION_REQUIRED')
            try:
                # First transaction statement. Dirty/nested callers fail; no silent rollback-and-proceed.
                cursor.execute('set transaction read only')
                source=cursor.var(oracledb.DB_TYPE_CLOB);source.setvalue(0,request.canonical_json())
                result=cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc('RRL_SHIPPING_GROSS_READ.freeze',[source,server_actor,result])
                raw=result.getvalue();raw=raw.read()if hasattr(raw,'read')else raw
                return parse_shipping_gross_read(raw,request)
            finally:
                connection.rollback();cursor.close()
