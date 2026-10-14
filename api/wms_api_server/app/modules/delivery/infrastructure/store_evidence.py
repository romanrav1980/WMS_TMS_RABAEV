"""Original photo BLOBs and immutable source association, outside stock commands."""
from hashlib import sha256
import json
from typing import Any
import oracledb
from ..contracts import StoreReceiptError
from ..contracts_evidence import ArchivedPhoto
from .photo_validation import verify_photo


def evidence_failure(error: oracledb.DatabaseError) -> StoreReceiptError:
    code=getattr(error.args[0],"code",0)
    return StoreReceiptError("PHOTO_ARCHIVE_REFUSED",str(error.args[0]).split("\n",1)[0],
                             403 if code==20882 else 409)


class StoreEvidence:
    def __init__(self, gateway: Any) -> None:
        self.gateway=gateway

    def upload(self, load_operation_id: str, store_address: str, view: str, mime_type: str, contents: bytes, actor: str) -> dict[str,Any]:
        width,height=verify_photo(contents,mime_type)
        try:
            with self.gateway.transaction("Archive original store receipt photo") as cursor:
                blob=cursor.var(oracledb.DB_TYPE_BLOB);blob.setvalue(0,contents)
                result=cursor.var(oracledb.DB_TYPE_CLOB)
                cursor.callproc("RRL_STORE_EVIDENCE_API.register_photo",
                    [load_operation_id,store_address,view,actor,mime_type,width,height,blob,result])
                value=result.getvalue();data=json.loads(value.read() if hasattr(value,"read") else value)
        except oracledb.DatabaseError as exc:
            if 20800<=abs(getattr(exc.args[0],"code",0))<=20999:
                raise evidence_failure(exc) from exc
            raise
        if data["sha256"]!=sha256(contents).hexdigest().upper():
            raise StoreReceiptError("PHOTO_CHECKSUM_CONFLICT","Контрольная сумма сохранённого фото не совпадает",503)
        return data

    def photos(self, load_operation_id: str, store_address: str, actor: str) -> list[dict[str,Any]]:
        try:
            rows=self.gateway.fetch_all("select RRL_STORE_EVIDENCE_API.photos_json(:op,:addr,:actor) PHOTOS from dual",
                                        {"op":load_operation_id,"addr":store_address,"actor":actor})
        except oracledb.DatabaseError as exc:
            if 20800<=abs(getattr(exc.args[0],"code",0))<=20999:
                raise evidence_failure(exc) from exc
            raise
        value=rows[0]["photos"]
        return value if isinstance(value,list) else json.loads(value)

    def content(self, photo_id: str, actor: str) -> ArchivedPhoto:
        rows=self.gateway.fetch_all("select LOAD_OPERATION_ID,STORE_ADDR from RRL_STORE_RECEIPT_PHOTO where PHOTO_ID=:id",{"id":photo_id})
        if len(rows)!=1:
            raise StoreReceiptError("PHOTO_NOT_FOUND","Фотография не найдена",404)
        self.photos(rows[0]["load_operation_id"],rows[0]["store_addr"],actor)
        data=self.gateway.fetch_all("""select asset.CONTENT_BYTES,asset.MIME_TYPE,asset.SHA256
            from RRL_STORE_RECEIPT_PHOTO photo join RRL_STORE_MEDIA_ASSET asset on asset.SHA256=photo.ASSET_SHA256
            where photo.PHOTO_ID=:id""",{"id":photo_id})[0]
        contents=data["content_bytes"]
        if not isinstance(contents,bytes) or sha256(contents).hexdigest().upper()!=data["sha256"]:
            raise StoreReceiptError("PHOTO_ARCHIVE_CHECKSUM_MISMATCH","Архив фотографии не прошёл проверку целостности",503)
        return ArchivedPhoto(contents,data["mime_type"],data["sha256"])
