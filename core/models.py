from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_specialisation = models
    department_head = models.Foreignkey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='head_departments'
    )
    
    def __str__(self):
        return self.department_name
    
class Team(models.Model):
    STATUS_CHOICES = [
      ('active', 'Active'),
      ('disband', 'Disbanded'),
      ('restructuring', 'Restructuring'),

    ]    
    team_name = models.CharField(max_length=100)
    team_purpose = models.TextField(blank=True)
    team_contactemail = models.EmailField(blank=True)
    manager = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='managed_teams'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DataTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.team_name
    
class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role_in_team = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.team.team_name}"
    
class CodeRepository(models.Model):
    repo_name = models.CharField(max_length=100)
    repo_url = models.URLField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='repositories')

    def __str__(self):
        return self.repo_name
    
class ContactChannel(models.Model):
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('phone', 'Phone'),
        ('other', 'Other'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='contact_channels')
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    contact_value = models.Charfield(max_length=200, blank=True)

    def __str__(self):
        return f"{self.channel_type}: {self.contact_value}"
    
class TeamDependency(models.Model):
    DEPENDENCY_Types = [
        ('upstream', 'Upstream'),
        ('downstream', 'Downstream'),
        
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='dependents')
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_Types)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('team', 'depends_on')

    def __str__(self):
        return f"{self.team.team_name} depends on {self.depends_on.team_name} ({self.dependency_type})"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL,)
    role = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'
    
class AuditLog(models.Model):
    User = models.ForeignKey(User, null= True, on_delete=models.SET_NULL)
    action_type = models.Charfield(max__length=20)
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.action_type} on {self.table_name} at {self.timestamp}'

