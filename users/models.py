from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
from django.utils import timezone
from datetime import timedelta

# ----------------------------
# Custom User Manager
# ----------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, name ,email, phone, password=None, user_type='client', **extra_fields):
        if not name:
            raise ValueError('Name is required')
        if not email:
            raise ValueError('Email is required')
        if not phone:
            raise ValueError('Phone is required')
        
        email = self.normalize_email(email)
        user = self.model(name=name,email=email, phone=phone, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(name,email, phone, password, user_type='admin', **extra_fields)

# ----------------------------
# Custom User Model
# ----------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_type_CHOICES = (
        ('admin','Admin'),
        ('client','Client'),
        ('employee','Employee'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=10, choices=user_type_CHOICES, default='client')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
   # last_login = models.DateTimeField(null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','phone']

    def __str__(self):
        return f"{self.name} ({self.user_type})"

# ----------------------------
# OTP Model
# ----------------------------
class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = random.randint(1000, 9999)  # 4-digit OTP
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.code} ({'expired' if self.is_expired() else 'active'})"
