import argon2
import random
import string
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from django.conf import settings


from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

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


class PasswordResetToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    @classmethod
    def generate_token(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_token(cls, email):
        cls.objects.filter(email=email).delete()
        
        token = cls.generate_token()
        return cls.objects.create(email=email, token=token)
    
    def is_valid(self):
        return (
            not self.is_used and 
            datetime.now() - self.created_at.replace(tzinfo=None) < timedelta(minutes=15)
        )
    
    def mark_as_used(self):
        self.is_used = True
        self.save()

    def send_reset_email(self):        
        account = Account.objects.get(email=self.email)
        
        subject = '重設密碼驗證碼'
        message = f'''親愛的 {account.username}，
            您請求重設密碼。請使用以下驗證碼來重設您的密碼：
            驗證碼：{self.token}
            此驗證碼將在 15 分鐘後過期。
            如果您沒有請求重設密碼，請忽略此郵件。
            謝謝！
            部落格團隊'''
        
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = self.email
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
