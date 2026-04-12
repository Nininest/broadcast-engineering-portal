from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'date_time', 'organizer', 'duration_minutes')
    list_filter = ('platform', 'date_time')
    search_fields = ('title', 'agenda')
    filter_horizontal = ('attendees',)
