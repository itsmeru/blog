from django.contrib.auth import get_user_model
from django.db import models

# from core.app.base.repository import BaseRepository

User = get_user_model()


class UserRepository():
    model_class = User

    @classmethod
    def create_user(cls, **kwargs) -> User:
        """Create a new user with the given fields."""
        return User.objects.create_user(**kwargs)

    @classmethod
    def get_by_email(cls, email: str) -> User:
        """Get a user by their email address."""
        return cls.get_by_field("email", email)

    @classmethod
    def get_by_phone(cls, phone: str) -> User:
        """Get a user by their phone number."""
        return cls.get_by_field("phone", phone)

    @classmethod
    def get_by_account(cls, account: str) -> User:
        """Get a user by either email or phone."""
        return cls.filter(models.Q(email=account) | models.Q(username=account)).first()

    @classmethod
    def update_password(cls, user: User, new_password: str) -> User:
        """Update a user's password."""
        user.set_password(new_password)
        user.save()
        return user

    @classmethod
    def get_active_users(cls) -> models.QuerySet[User]:
        """Get all active users."""
        return cls.filter(is_active=True)

    @classmethod
    def deactivate_user(cls, user: User) -> User:
        """Deactivate a user account."""
        return cls.update(user, is_active=False)

    @classmethod
    def activate_user(cls, user: User) -> User:
        """Activate a user account."""
        return cls.update(user, is_active=True)

    @classmethod
    def get_users_with_filters(cls, department=None, is_active=None, search=None):
        """Get users with optional filters for department, status and search."""
        queryset = cls._base_query().select_related().prefetch_related("roles")

        if department:
            queryset = queryset.filter(department=department)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if search:
            queryset = queryset.filter(
                models.Q(nickname__icontains=search)
                | models.Q(username__icontains=search)
            )

        return queryset.order_by("-created_at")

    @classmethod
    def get_user_by_id_with_relations(cls, user_id: int):
        """Get user by ID with all related data loaded."""
        return (
            cls._base_query()
            .select_related()
            .prefetch_related("roles", "permissions", "roles__permissions")
            .filter(id=user_id)
            .first()
        )

    @classmethod
    def hard_delete_user(cls, user: User) -> None:
        """Hard delete a user (permanent deletion)."""
        user.delete()
