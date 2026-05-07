from django.db import models
from django.contrib.auth.models import User


class Meeting(models.Model):
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('google_meet', 'Google Meet'),
        ('in_person', 'In Person'),
        ('phone', 'Phone Call'),
    ]

    title = models.CharField(max_length=200)
    agenda = models.TextField(blank=True)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='zoom')
    meeting_link = models.URLField(blank=True)
    date_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    attendees = models.ManyToManyField(User, related_name='meetings', blank=True)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_meetings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']

    def __str__(self):
        return f"{self.title} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"
