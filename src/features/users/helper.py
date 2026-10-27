from src.constants import SortType
from src.db.models import User


USER_SORT_HELPER = {
    SortType.LAST_NAME: User.last_name,
    SortType.EMAIL: User.email,
    SortType.CREATED_AT: User.created_at
}
