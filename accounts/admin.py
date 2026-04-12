# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone', 'department', 'bio', 'profile_picture')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display  = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter   = ('is_staff', 'is_superuser', 'profile__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display   = ('user', 'role', 'department', 'phone', 'date_joined')
    list_filter    = ('role', 'department')
    search_fields  = ('user__username', 'user__email', 'department')
    readonly_fields = ('date_joined', 'last_updated')
    fieldsets = (
        ('User',         {'fields': ('user',)}),
        ('Profile Info', {'fields': ('role', 'phone', 'department', 'bio', 'profile_picture')}),
        ('Timestamps',   {'fields': ('date_joined', 'last_updated'), 'classes': ('collapse',)}),
    )