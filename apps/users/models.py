from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # --- Django 認證系統預設必須欄位 ---
    email = models.EmailField(
        _("電子郵件"), unique=True, null=True, blank=True
    )  # USERNAME_FIELD
    is_active = models.BooleanField(_("是否啟用"), default=True)  # 必須
    is_staff = models.BooleanField(
        _("是否為工作人員"), default=False
    )  # 必須（admin 權限）
    # PermissionsMixin 會自動加上 is_superuser, groups, user_permissions

    # --- 你自訂的商業邏輯欄位 ---
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nickname = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enabled_permissions = models.JSONField(_("啟用的權限"), default=list, blank=True)
    disabled_permissions = models.JSONField(_("停用的權限"), default=list, blank=True)
    # roles = models.ManyToManyField("rbac.Role", related_name="users", blank=True)
    # permissions = models.ManyToManyField(
    #     "rbac.Permission", related_name="users", blank=True
    # )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.nickname or self.email or str(self.id)

    class Meta:
        verbose_name = _("使用者")
        verbose_name_plural = _("使用者")
