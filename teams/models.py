from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    """
    Central model representing an engineering team at Sky.
    Stores all discoverable information an engineer needs to find and contact a team.
    """
    LIFECYCLE_CHOICES = [
        ('active', 'Active'),
        ('disbanded', 'Disbanded'),
        ('merged', 'Merged'),
        ('reformed', 'Reformed'),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    mission = models.TextField(blank=True, help_text="Team mission statement")
    responsibilities = models.TextField(blank=True)

    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_teams'
    )

    # Department is stored as text so the teams app runs independently;
    # it will be a ForeignKey once the organization app is merged.
    department_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Department name (will be linked to org app on merge)"
    )

    # Contact channels
    slack_channel = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    code_repository = models.URLField(blank=True)

    # Lifecycle
    lifecycle_status = models.CharField(
        max_length=20,
        choices=LIFECYCLE_CHOICES,
        default='active'
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Upstream  = teams this team depends ON (providers)
    # Downstream = teams that depend on us (auto reverse via downstream_dependents)
    upstream_dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='downstream_dependents',
        help_text="Teams that this team depends on (upstream providers)"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class TeamMember(models.Model):
    """Links a Django User to a Team with a specific role."""
    ROLE_CHOICES = [
        ('engineer', 'Engineer'),
        ('senior_engineer', 'Senior Engineer'),
        ('lead', 'Tech Lead'),
        ('manager', 'Manager'),
        ('other', 'Other'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='engineer')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user.get_full_name() or self.user.username} – "
            f"{self.team.name} ({self.get_role_display()})"
        )

    class Meta:
        unique_together = ('team', 'user')
        ordering = ['team', 'role']


class TeamSkill(models.Model):
    """A technology or skill tag associated with a team (e.g. Python, Kubernetes)."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.team.name}: {self.name}"

    class Meta:
        unique_together = ('team', 'name')
        ordering = ['name']
