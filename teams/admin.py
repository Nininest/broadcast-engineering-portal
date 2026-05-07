from django.contrib import admin
from .models import Team, TeamMember, TeamSkill


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ('user', 'role')


class TeamSkillInline(admin.TabularInline):
    model = TeamSkill
    extra = 2
    fields = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'department_name', 'manager',
        'email', 'is_active', 'member_count', 'created_at'
    )
    list_filter = ('is_active', 'department_name')
    search_fields = ('name', 'description', 'mission', 'email', 'department_name')
    filter_horizontal = ('upstream_dependencies',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TeamMemberInline, TeamSkillInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'department_name', 'manager', 'is_active')
        }),
        ('Details', {
            'fields': ('mission', 'description', 'responsibilities')
        }),
        ('Contact & Links', {
            'fields': ('email', 'slack_channel', 'code_repository')
        }),
        ('Dependencies', {
            'fields': ('upstream_dependencies',),
            'description': 'Select teams that this team depends on (upstream providers).'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role', 'joined_at')
    list_filter = ('team', 'role')
    search_fields = (
        'user__username', 'user__first_name',
        'user__last_name', 'team__name'
    )


@admin.register(TeamSkill)
class TeamSkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'team')
    list_filter = ('team',)
    search_fields = ('name', 'team__name')
