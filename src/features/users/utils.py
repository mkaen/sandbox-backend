
from src.constants import UserRoles
from src.db.models import User



def create_deactivated_email(id, email):
    return f"deleted_{id}_{email}"


def handle_role_change_permission(role: UserRoles, current_user: User, user: User) -> bool:
    return user.role != role and current_user.role == UserRoles.ADMIN
