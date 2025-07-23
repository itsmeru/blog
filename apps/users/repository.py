from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserRepository:
    @staticmethod
    def create_user(**kwargs):
        return User.objects.create_user(**kwargs)

    @staticmethod
    def get_by_email(email):
        return User.objects.filter(email=email).first()

    @staticmethod
    def get_by_phone(phone):
        return User.objects.filter(phone=phone).first()

    @staticmethod
    def get_by_account(account):
        return User.objects.filter(Q(email=account) | Q(username=account)).first()

    @staticmethod
    def update_password(user, new_password):
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def get_active_users():
        return User.objects.filter(is_active=True)

    @staticmethod
    def deactivate_user(user):
        user.is_active = False
        user.save()
        return user

    @staticmethod
    def activate_user(user):
        user.is_active = True
        user.save()
        return user

    @staticmethod
    def get_users_with_filters(department=None, is_active=None, search=None):
        queryset = User.objects.all()

        if department:
            queryset = queryset.filter(department=department)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if search:
            queryset = queryset.filter(
                Q(nickname__icontains=search) | Q(username__icontains=search)
            )

        return queryset.order_by("-created_at")

    @staticmethod
    def get_user_by_id_with_relations(user_id):
        return (
            User.objects.select_related()
            .prefetch_related("roles", "permissions", "roles__permissions")
            .filter(id=user_id)
            .first()
        )

    @staticmethod
    def hard_delete_user(user):
        user.delete()
        return True
