"""Bounded full decoding, preserving original bytes for evidence."""
from io import BytesIO
from PIL import Image,UnidentifiedImageError
from ..contracts import StoreReceiptError

MAX_PHOTO_BYTES=4*1024*1024
MAX_PHOTO_PIXELS=12_000_000


def verify_photo(contents: bytes, mime_type: str) -> tuple[int,int]:
    if not contents or len(contents)>MAX_PHOTO_BYTES:
        raise StoreReceiptError("PHOTO_SIZE_INVALID","Размер фотографии должен быть от 1 байта до 4 МиБ",422)
    try:
        with Image.open(BytesIO(contents),formats=("JPEG","PNG")) as image:
            width,height=image.size
            actual_mime={"JPEG":"image/jpeg","PNG":"image/png"}.get(image.format or "")
            if actual_mime!=mime_type or getattr(image,"n_frames",1)!=1:
                raise StoreReceiptError("PHOTO_FORMAT_INVALID","Нужна одна фотография JPEG или PNG указанного формата",422)
            if min(width,height)<160 or width*height<320*240 or width*height>MAX_PHOTO_PIXELS:
                raise StoreReceiptError("PHOTO_DIMENSIONS_INVALID","Недопустимое разрешение фотографии: до 12 мегапикселей",422)
            image.verify()
        with Image.open(BytesIO(contents),formats=("JPEG","PNG")) as image:
            image.load()
        return width,height
    except (UnidentifiedImageError,OSError,ValueError,Image.DecompressionBombError) as exc:
        raise StoreReceiptError("PHOTO_CONTENT_INVALID","Фотография повреждена или имеет неподдерживаемый формат",422) from exc
