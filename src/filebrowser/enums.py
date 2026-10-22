from enum import Enum, StrEnum


class ErrorMessage(Enum):
    INVALID_REQUEST = "Invalid Request", 400
    USER_NOT_FOUND = "User Not Found", 404
    EXPIRED = "Expired Request", 403
    USER_EXISTS = "User Exists", 409
    AUTHENTICATION = "You don't have access", 401
    NO_SCOPES = "You don't have access to any scopes", 403
    PATH_NOT_FOUND = "Path Not Found", 404

class SuccessMessage(Enum):
    LOGIN = "Successful Login", 200
    REGISTRATION = "Successful Registration", 200
    LOGOUT = "Successful Logout", 200

class Permission(StrEnum):
    DOWNLOAD = "download"
    UPLOAD = "upload"
    VIEW = "view"
    DELETE = "delete"
    ADMIN = "admin"

class EntryType(StrEnum):
    VIDEO = "video"
    IMAGE = "image"
    FOLDER = "folder"
    OTHER = "other"