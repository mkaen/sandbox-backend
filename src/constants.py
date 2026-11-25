from enum import Enum

class UserRoles(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class SortType(Enum):
    LAST_NAME = "lastName"
    EMAIL = "email"
    CREATED_AT = "created_at"


class SortOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ImageTypesFolderName(Enum):
    PROFILE = "profile_images"

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 30

DEFAULT_SORT = SortType.CREATED_AT

POPULAR_CRYPTO_ASSETS = ["bitcoin", "ethereum", "solana", "sui"]


CACHE_TIME = {
    "CG_popular_asset_refresh": 15,
    "CG_fear_and_greed_index_refresh": 10
}

class CryptoSentiment(Enum):
    EXTREME_FEAR = "EXTREME_FEAR"
    FEAR = "FEAR"
    NEUTRAL = "NEUTRAL"
    GREED = "GREED"
    EXTREME_GREED = "EXTREME_GREED"
