# Generated by Django 5.2.4 on 2025-07-23 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        unique=True,
                        verbose_name="電子郵件",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="是否啟用"),
                ),
                (
                    "is_staff",
                    models.BooleanField(default=False, verbose_name="是否為工作人員"),
                ),
                (
                    "phone",
                    models.CharField(blank=True, max_length=20, null=True, unique=True),
                ),
                ("nickname", models.CharField(max_length=50)),
                (
                    "username",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                ("password", models.CharField(max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "enabled_permissions",
                    models.JSONField(
                        blank=True, default=list, verbose_name="啟用的權限"
                    ),
                ),
                (
                    "disabled_permissions",
                    models.JSONField(
                        blank=True, default=list, verbose_name="停用的權限"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "使用者",
                "verbose_name_plural": "使用者",
            },
        ),
    ]
