from django.contrib import admin
from .models import Department, Team, TeamMembership, CodeRepository, ContactChannel,  TeamDependency, UserProfile, Audiotlog

admin.site.site_header = "Broadcast Engineering Teams Admin"
title = "Broadcast Engineering Teams Admin"

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department_name', 'department_specialization', 'department_head']
    search_fields = ['department_name']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'department', ' manager', 'status']
    list_filter = ['status', 'department']
    search_fields = ['team_name', 'team_purpose']

@admin.register(TeamMembership)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role_in_team']
    list_filter = ['team']

@admin.register(CodeRepository)
class CodeRepositoryAdmin(admin.ModelAdmin):
    list_display = ['repo_name', 'team', 'repo_uri']

@admin.register(ContactChannel)
class ContactChannelAdmin(admin.ModelAdmin):
    list_display = ['team', 'channel_type', 'contact_value']

@admin.register(TeamDependency)
class TeamDependencyAdmin(admin.ModelAdmin):
    list_display = ['team', 'depends_on', 'dependency_type']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department']

@admin.register(Audiotlog)
class AudiotlogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'table_name', 'timestamp']
    list_filter = ['action_type']
    readonly_fields = ['user', 'action_type', 'table_name', 'reord_id', 'timestamp']



