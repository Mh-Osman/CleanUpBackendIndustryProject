# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# import random
# from django.utils import timezone
# from datetime import timedelta

# # ----------------------------
# # Custom User Manager
# # ----------------------------
# class CustomUserManager(BaseUserManager):
#     def create_user(self, name ,email, prime_phone, password=None, user_type='client', **extra_fields):
#         if not name:
#             raise ValueError('Name is required')
#         if not email:
#             raise ValueError('Email is required')
#         if not prime_phone:
#             raise ValueError('prime_phone is required')
        
#         email = self.normalize_email(email)
#         user = self.model(name=name,email=email, prime_phone=prime_phone, user_type=user_type, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, name, email, prime_phone, password=None, **extra_fields):
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#         return self.create_user(name,email, prime_phone, password, user_type='admin', **extra_fields)

# # ----------------------------
# # Custom User Model
# # ----------------------------
# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     user_type_CHOICES = (
#         ('admin','Admin'),
#         ('client','Client'),
#         ('employee','Employee'),
#         ('supervisor','Supervisor'),
#     )
#     name = models.CharField(max_length=255)
#     username = models.CharField(max_length=255, unique=True, null=True, blank=True)
#     email = models.EmailField(unique=True)
#     prime_phone = models.CharField(max_length=15, unique=True)
#     user_type = models.CharField(max_length=10, choices=user_type_CHOICES, default='client')
#     is_active = models.BooleanField(default=False)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     is_suspended = models.BooleanField(default=False)
#     date_joined = models.DateTimeField(auto_now_add=True)
#     last_login = models.DateTimeField(null=True, blank=True)
#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['name','prime_phone']

#     def __str__(self):
#         return f"{self.name} ({self.user_type} {self.id})"

# # ----------------------------
# # OTP Model
# # ----------------------------
# class OTP(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
#     code = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()

#     def save(self, *args, **kwargs):
#         OTP.objects.filter(expires_at__lt=timezone.now()).delete()
#         if not self.code:
#             self.code = random.randint(1000, 9999)  # 4-digit OTP
#         if not self.expires_at:
#             self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
#         super().save(*args, **kwargs)

#     def is_expired(self):
#         return timezone.now() > self.expires_at

#     def __str__(self):
#         return f"{self.user.email} - {self.code} ({'expired' if self.is_expired() else 'active'})"

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
from django.utils import timezone
from datetime import timedelta

# ----------------------------
# Custom User Manager
# ----------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, prime_phone, password=None, user_type='client', username=None, **extra_fields):
        if not name:
            raise ValueError('Name is required')
        if not email:
            raise ValueError('Email is required')
        if not prime_phone:
            raise ValueError('prime_phone is required')
        
        email = self.normalize_email(email)
        
        # Generate a unique username if not provided
        if not username:
            username = self.generate_unique_username(name)
        
        user = self.model(
            name=name,
            email=email,
            prime_phone=prime_phone,
            user_type=user_type,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, prime_phone, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(name, email, prime_phone, password, user_type='admin', **extra_fields)

    def generate_unique_username(self, name):
        """
        Generate a unique username using the name + random 10-digit number.
        """
        for _ in range(10):  # try 10 times
            username_candidate = f"{name.lower()}{random.randint(1000000000, 9999999999)}"
            if not CustomUser.objects.filter(username=username_candidate).exists():
                return username_candidate
        raise ValueError("Unable to generate a unique username. Try again.")

# ----------------------------
# Custom User Model
# ----------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_type_CHOICES = (
        ('admin','Admin'),
        ('client','Client'),
        ('employee','Employee'),
        ('supervisor','Supervisor'),
    )

    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    prime_phone = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=10, choices=user_type_CHOICES, default='client')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'prime_phone']

    def save(self, *args, **kwargs):
        # Auto-generate username if not provided
        if not self.username:
            self.username = CustomUserManager().generate_unique_username(self.name)
            if self.user_type == 'admin':
                
                self.is_superuser = True
                self.is_staff = True
            else:
                self.is_superuser = False
                self.is_staff = False
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user_type} {self.id})"


# ----------------------------
# OTP Model
# ----------------------------
class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Delete expired OTPs
        OTP.objects.filter(expires_at__lt=timezone.now()).delete()
        
        # Generate 4-digit code if not provided
        if not self.code:
            self.code = random.randint(1000, 9999)
        
        # Set expiry if not provided (10 minutes from now)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.code} ({'expired' if self.is_expired() else 'active'})"
