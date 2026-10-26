from src.constants import SortType
from src.db.models import User


USER_SORT_HELPER = {
    "last_name": User.last_name,
    "email": User.email,
    "created_at": User.created_at
}

SERIALIZED_USER_SORT_TYPE = {
    "last_name": SortType.LAST_NAME,
    "email": SortType.EMAIL
}


