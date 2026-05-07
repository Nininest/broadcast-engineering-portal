from django.db import models


class Department(models.Model):
    

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the department (e.g. 'Broadcast Engineering')"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of the department's responsibilities"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the department record was created"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name

    def get_team_count(self):
        """Returns the number of teams belonging to this department."""
       
        return self.team_members.values('team_name').distinct().count()


class Organisation(models.Model):
    

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the organisation (e.g. 'Sky Broadcasting Ltd')"
    )
    departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='organisations',
        help_text="Departments that belong to this organisation"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Organisation'
        verbose_name_plural = 'Organisations'

    def __str__(self):
        return self.name
