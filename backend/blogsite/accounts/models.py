import hashlib
import os

from django.db import models


# Create your models here.
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
        salt = os.urandom(16)  # 改為 16 bytes
        password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        self.password = salt.hex() + password_hash.hex()

    def check_password(self, password):
        stored_data = bytes.fromhex(self.password)
        salt = stored_data[:16]  # 前 16 bytes 是鹽值
        stored_hash = stored_data[16:]  # 剩餘的是雜湊值
        input_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return stored_hash == input_hash
