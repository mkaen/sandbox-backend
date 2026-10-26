from enum import Enum

class UserRoles(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class SortType(Enum):
    LAST_NAME = "last_name"
    EMAIL = "email"


class SortOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ImageTypesFolderName(Enum):
    PROFILE = "profile_images"

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 30
