"""Server object-author check executed within the caller's locked business transaction."""
from typing import Any
import oracledb

def assert_independent_decision(cursor: Any, actor: str, author: str, process: str) -> None:
    cursor.callproc("RRL_ACCESS_API.assert_independent",[actor,author,process])
