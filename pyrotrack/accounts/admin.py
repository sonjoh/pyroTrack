from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # Add and remove fields as necessary
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'invited_by')}),
        (('Status fields'), {'fields': ('is_active', 'is_staff','is_banned', 'banned_reason', 'ban_date', 'is_verified', 'is_premium', 'is_donator', 'is_uploader')}),
        (('Ratio fields'), {'fields': ('uploaded', 'downloaded', 'ratio')}),
        (('Permissions'), {'fields': ( 'is_superuser', 'groups', 'user_permissions')}),
    )
    # Add and remove fields as necessary
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin)