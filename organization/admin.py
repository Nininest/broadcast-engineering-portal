from django.contrib import admin
from .models import Department, Organisation


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    
    
    list_display = ('name', 'short_description', 'created_at')

    search_fields = ('name', 'description')

    list_filter = ('created_at',)

    readonly_fields = ('created_at',)

    ordering = ('name',)

    def short_description(self, obj):
        """Returns a truncated version of the description for the list view."""
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description

    short_description.short_description = 'Description'


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):

    list_display = ('name', 'department_count')
    search_fields = ('name',)
   
    filter_horizontal = ('departments',)

    def department_count(self, obj):
        """Returns the number of departments linked to this organisation."""
        return obj.departments.count()

    department_count.short_description = 'No. of Departments'
