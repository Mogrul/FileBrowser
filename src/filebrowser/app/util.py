from flask import url_for

from filebrowser.enums import ErrorMessage, SuccessMessage, EntryType
from filebrowser.models import FileEntry


def send_error(
        message: str | ErrorMessage,
        code: int | None = None,
        **data
) -> tuple[dict, int]:
    if isinstance(message, ErrorMessage):
        message, code = message.value

    elif code is None:
        raise RuntimeError("Used message in send_error as a string without code")

    return {
        "success": False,
        "message": message,
        "data": { **data }
    }, code

def send_success(
        message: str | SuccessMessage,
        code: int | None = None,
        **data
) -> tuple[dict, int]:
    if isinstance(message, SuccessMessage):
        message, code = message.value

    elif code is None:
        raise RuntimeError("Used message in send_success as a string without code")

    return {
        "success": True,
        "message": message,
        "data": data.get("data", data)
    }, code

def get_entry_url(entry: FileEntry, scope_name: str | None) -> str:
    match entry.type:
        case EntryType.FOLDER:
            return url_for("index.index", scope=scope_name, path=entry.id)

        case EntryType.IMAGE:
            return url_for("api.files.image", path=entry.id)

        case EntryType.VIDEO:
            return url_for("api.files.video", path=entry.id)

        case EntryType.OTHER:
            return url_for("api.files.other", path=entry.id)

        case _:
            raise RuntimeError(f"Unknown entry type: {entry.type}")
