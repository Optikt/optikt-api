from typing import List
from fastapi import HTTPException, status
from app.models.enums import UserRole


class RoleChecker:
    """Verifica que el usuario tenga uno de los roles permitidos"""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_role: str) -> bool:
        if user_role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acción",
            )
        return True


# Decoradores predefinidos para facilitar el uso
def require_super_admin(user_role: str):
    """Solo SUPER_ADMIN"""
    return RoleChecker([UserRole.SUPER_ADMIN])(user_role)


def require_admin(user_role: str):
    """SUPER_ADMIN o ADMIN"""
    return RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN])(user_role)


def require_manager(user_role: str):
    """SUPER_ADMIN, ADMIN o MANAGER"""
    return RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER])(
        user_role
    )


def require_seller(user_role: str):
    """Cualquier rol excepto VIEWER"""
    return RoleChecker(
        [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER, UserRole.SELLER]
    )(user_role)
