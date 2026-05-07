 Organization Module — Broadcast Engineering Portal
Author: Sushma
Branch: features/sushma_organization
Module: 5COSC021W — Coursework 2 (2025/26)
App: organization
Framework: Django + SQLite

Table of Contents

Overview
Files in This Module
Database Models
URL Routes
Views
Templates
How to Set Up
How to Run
Testing
Commit History
Dependencies


Overview
The Organization module handles the structural hierarchy of the Broadcast Engineering Portal. It allows authenticated users to:

Browse all departments in the organisation
View teams belonging to each department
See the full org chart (Organisation → Departments → Teams)
Explore an interactive dependency graph showing connections between teams

This module integrates with the teams app (Yujala's module) to display team data within departments.

Files in This Module
organization/
├── models.py                          → Department & Organisation database models
├── admin.py                           → Admin panel registration
├── urls.py                            → URL routing (4 routes)
├── views.py                           → View logic for all 4 pages
└── migrations/
    └── 0001_initial.py                → Auto-generated after makemigrations

templates/organization/
├── department_list.html               → Cards grid of all departments
├── department_detail.html             → Teams listed under one department
├── org_chart.html                     → Collapsible tree: Org → Depts → Teams
└── dependency_graph.html              → Interactive D3.js team dependency graph

Database Models
Department
Represents a single business unit within the organisation.
FieldTypeDescriptionidAutoField (PK)Auto-generated primary keynameCharField(200)Department name — uniquedescriptionTextFieldOptional description of the departmentcreated_atDateTimeFieldTimestamp set automatically on creation
pythonclass Department(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

Organisation
Wraps multiple departments into one top-level organisation unit. Used for the org chart and dependency graph views.
FieldTypeDescriptionidAutoField (PK)Auto-generated primary keynameCharField(200)Organisation name — uniquedepartmentsManyToManyFieldLinked departments (flexible, no schema changes needed to add more)
pythonclass Organisation(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    departments = models.ManyToManyField(Department, blank=True)

Why ManyToMany? A department could theoretically belong to multiple organisations. This design is flexible and future-proof — adding new departments to an organisation requires no database schema changes.


URL Routes
All routes require the user to be logged in (@login_required).
URLView FunctionNameDescription/organization/departments/department_listorganization:department_listAll departments as cards/organization/departments/<int:pk>/department_detailorganization:department_detailOne department's teams/organization/org-chart/org_chartorganization:org_chartFull org hierarchy tree/organization/dependency-graph/dependency_graphorganization:dependency_graphTeam dependency graph
Namespace: organization (set in urls.py via app_name = 'organization')
Use in templates like:
html<a href="{% url 'organization:department_list' %}">Departments</a>
<a href="{% url 'organization:department_detail' dept.pk %}">View</a>

Views
department_list(request)

Queries all Department objects
Annotates each with a team_count (number of distinct teams)
Renders organization/department_list.html

department_detail(request, pk)

Fetches one Department by primary key using get_object_or_404
Queries all TeamMember objects linked to that department
Renders organization/department_detail.html

org_chart(request)

Fetches all Organisation objects with prefetch_related('departments')
Builds a nested Python list (org_data) for the template
Renders organization/org_chart.html

dependency_graph(request)

Builds JSON-serialisable nodes and edges lists
Nodes = distinct team names; Edges = upstream/downstream repo dependencies
Passes nodes_json and edges_json to organization/dependency_graph.html


Templates
department_list.html

Bootstrap card grid (responsive: 1 → 2 → 3 columns)
Each card shows: department name, description preview, team count badge, View button
Hover animation (card lifts on mouse-over)
Empty state: shows friendly message if no departments exist

department_detail.html

Breadcrumb navigation back to department list
Header card with department name, description, creation date
Team list as cards with contact email and link to team detail
Empty state if no teams are assigned

org_chart.html

Collapsible tree using Bootstrap Collapse + CSS connecting lines
Levels: Organisation (blue) → Department (teal) → Team (green)
Expand All / Collapse All buttons
Department names link directly to their detail page

dependency_graph.html

Interactive D3.js v7 force-directed graph
Nodes coloured by department group using d3.scaleOrdinal(d3.schemeTableau10)
Drag nodes, scroll to zoom, reset zoom button
Tooltip shows team name and department on hover
Directed edges with arrow markers showing dependency direction
Empty state if no team data available


How to Set Up
1. Clone the repository
bashgit clone https://github.com/Nininest/broadcast-engineering-portal.git
cd broadcast-engineering-portal
2. Create and activate virtual environment
bash# Create
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — Mac/Linux
source venv/bin/activate
3. Install dependencies
bashpip install -r requirements.txt
4. Switch to Sushma's branch
bashgit checkout features/sushma_organization
5. Place the files in the correct locations
broadcast-engineering-portal/
├── organization/
│   ├── __init__.py       ← create empty file
│   ├── models.py         ← from this module
│   ├── admin.py          ← from this module
│   ├── urls.py           ← from this module
│   ├── views.py          ← from this module
│   ├── apps.py           ← create (see below)
│   └── migrations/
│       └── __init__.py   ← create empty file
└── templates/
    └── organization/
        ├── department_list.html
        ├── department_detail.html
        ├── org_chart.html
        └── dependency_graph.html
Create organization/apps.py:
pythonfrom django.apps import AppConfig

class OrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'organization'
6. Register the app in settings.py
pythonINSTALLED_APPS = [
    ...
    'organization',   # ← add this
]
Make sure TEMPLATES includes the templates folder:
pythonTEMPLATES = [{
    ...
    'DIRS': [BASE_DIR / 'templates'],
    ...
}]
7. Add URLs to the main urls.py
pythonfrom django.urls import path, include

urlpatterns = [
    ...
    path('organization/', include('organization.urls', namespace='organization')),
]
8. Run migrations
bashpython manage.py makemigrations organization
python manage.py migrate
9. Create a superuser (if not already done)
bashpython manage.py createsuperuser
10. Add test data via admin
http://127.0.0.1:8000/admin/organization/department/add/
http://127.0.0.1:8000/admin/organization/organisation/add/

How to Run
bashpython manage.py runserver
Then open your browser:
PageURLDepartment Listhttp://127.0.0.1:8000/organization/departments/Org Charthttp://127.0.0.1:8000/organization/org-chart/Dependency Graphhttp://127.0.0.1:8000/organization/dependency-graph/Admin Panelhttp://127.0.0.1:8000/admin/

All pages require login. Use the superuser account you created above.


Testing
Manual test cases for this module:
Test IDDescriptionExpected ResultTC-ORG-01Load /organization/departments/All departments shown as cards with team countTC-ORG-02Click a department cardDepartment detail page shows correct teamsTC-ORG-03Load /organization/org-chart/Tree renders: Organisation → Departments → TeamsTC-ORG-04Load /organization/dependency-graph/D3 graph renders with nodes and edgesTC-ORG-05Visit any page while logged outRedirected to login pageTC-ORG-06No departments in databaseDepartment list shows "No departments found"TC-ORG-07Add department via adminAppears on department list pageTC-ORG-08Add organisation via adminAppears on org chart

Commit History
All commits made on branch features/sushma_organization:
#FileCommit MessageDateTime1organization/models.pyAdded Department and Organisation modelsApril 10, 20262:19:44 PM2organization/admin.pyRegistered Department model in adminApril 12, 202611:38:22 AM3organization/urls.pyAdded URL paths for department list, detail, org chart and dependency graphApril 14, 202610:35:28 AM4organization/views.pyWrote department list, department detail, org chart and dependency graph viewsApril 16, 20269:48:33 AM5templates/organization/department_list.htmlCreated department list template with team count cardsApril 18, 20263:14:57 PM6templates/organization/department_detail.htmlCreated department detail template showing all teams under departmentApril 20, 202611:22:41 AM7templates/organization/org_chart.htmlCreated org chart template with departments and nested teams treeApril 22, 20262:46:19 PM8templates/organization/dependency_graph.htmlCreated global dependency graph template showing all team connectionsApril 24, 202610:14:37 AM

Dependencies
Python / Django
PackagePurposeDjangoWeb framework — models, views, templates, ORMsqlite3Default Django database (built-in, no install needed)
Frontend (loaded via CDN — no install needed)
LibraryVersionPurposeBootstrap5.xResponsive layout, cards, badges, collapseBootstrap Icons1.xIcons throughout the UID3.js7.8.5Interactive force-directed dependency graph
Integration
AppHow it connectsteams (Yujala)TeamMember model queried in department_detail and dependency_graph views via ForeignKey to Departmentaccounts (Palisha)@login_required uses Django's auth system set up in the accounts app

