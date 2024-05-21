from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    # Add any additional fields here
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)  # This should be is_active, not isActive
    is_staff = models.BooleanField(default=False)  # This should be is_staff, not isStaff
    is_superuser = models.BooleanField(default=False)  # This should be is_superuser, not isSuperuser

    is_banned = models.BooleanField(default=False)
    banned_reason = models.TextField(null=True, blank=True)
    ban_date = models.DateTimeField(null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_donator = models.BooleanField(default=False)
    is_uploader = models.BooleanField(default=False)

    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    ratio = models.FloatField(default=0.0)
    uploaded = models.BigIntegerField(default=0)
    downloaded = models.BigIntegerField(default=0)

    REQUIRED_FIELDS = ['email']

    # Add custom related_name to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text=('The groups this user belongs to. '
                   'A user will get all permissions granted to each of '
                   'their groups.'),
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        return self.username
