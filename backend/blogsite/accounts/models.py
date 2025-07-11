import argon2

from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "password"]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.username

    def set_password(self, password):
        ph = argon2.PasswordHasher(
            time_cost=4,
            memory_cost=65535,
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )
        self.password = ph.hash(password)

    def check_password(self, password):
        ph = argon2.PasswordHasher()

        try:
            ph.verify(self.password, password)
        except (
            argon2.exceptions.VerifyMismatchError,
            argon2.exceptions.VerificationError,
        ):
            return False

        return True