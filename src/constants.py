from enum import Enum

class UserRoles(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class ImageTypesFolderName(Enum):
    PROFILE = "profile_images"

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 30
