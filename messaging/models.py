from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    STATUS_CHOICES = [
        ('draft','Draft'),
        ('sent','Sent'),
    ]
sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')#
recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')#
subject = models.CharField(max_length=255)
body = models.TextField()
status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
created_at = models.DateTimeField(auto_now_add=True)
read = models.BooleanField(default=False)
deleted_by_sender = models.BooleanField(default=False)
deleted_by_recipient = models.BooleanField(default=False)

def __str__(self):
    return f"{self.subject} [{self.sender} -> {self.recipient}]"

class Meta:
    ordering = ['-created_at']