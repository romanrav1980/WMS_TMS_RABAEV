"""Stable web asset MIME types despite Windows registry file associations."""
import mimetypes


def register_web_media_types() -> None:
    # Initialize registry mappings first, then override only web runtime formats.
    if not mimetypes.inited:
        mimetypes.init()
    for suffix, media_type in ((".js", "text/javascript"), (".mjs", "text/javascript"),
                               (".css", "text/css"), (".svg", "image/svg+xml"),
                               (".webmanifest", "application/manifest+json"), (".wasm", "application/wasm")):
        mimetypes.add_type(media_type, suffix, strict=True)
