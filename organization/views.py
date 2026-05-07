import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import Department, Organisation

try:
    from teams.models import TeamMember
    TEAMS_AVAILABLE = True
except ImportError:
    TEAMS_AVAILABLE = False


@login_required
def department_list(request):
   
    if TEAMS_AVAILABLE:
        departments = Department.objects.annotate(
            team_count=Count('team_members__team_name', distinct=True)
        ).order_by('name')
    else:
        departments = Department.objects.all().order_by('name')

    context = {
        'departments': departments,
        'page_title': 'Departments',
    }
    return render(request, 'organization/department_list.html', context)


@login_required
def department_detail(request, pk):
    
    department = get_object_or_404(Department, pk=pk)

    if TEAMS_AVAILABLE:
        teams = TeamMember.objects.filter(
            department=department
        ).values(
            'team_name', 'contact_email'
        ).distinct().order_by('team_name')
    else:
        teams = []

    context = {
        'department': department,
        'teams': teams,
        'page_title': department.name,
    }
    return render(request, 'organization/department_detail.html', context)


@login_required
def org_chart(request):
    
    organisations = Organisation.objects.prefetch_related(
        'departments'
    ).all().order_by('name')

    org_data = []
    for org in organisations:
        dept_list = []
        for dept in org.departments.all():
            if TEAMS_AVAILABLE:
                teams = list(
                    TeamMember.objects.filter(department=dept)
                    .values('team_name')
                    .distinct()
                    .order_by('team_name')
                )
            else:
                teams = []

            dept_list.append({
                'id': dept.pk,
                'name': dept.name,
                'description': dept.description,
                'teams': teams,
            })

        org_data.append({
            'name': org.name,
            'departments': dept_list,
        })

    context = {
        'org_data': org_data,
        'page_title': 'Organisation Chart',
    }
    return render(request, 'organization/org_chart.html', context)


@login_required
def dependency_graph(request):
   
    nodes = []
    edges = []
    node_index = {}  # maps team_name -> node id

    if TEAMS_AVAILABLE:

        teams = TeamMember.objects.values('team_name', 'department__name').distinct()
        for i, team in enumerate(teams):
            node_index[team['team_name']] = i
            nodes.append({
                'id': i,
                'label': team['team_name'],
                'group': team['department__name'] or 'Unassigned',
            })

    
        try:
            from teams.models import CodeRepository
            repos = CodeRepository.objects.select_related('team').all()
            for repo in repos:
                # Each repo's upstream dependencies create an edge
                for dep in repo.upstream_dependencies.all():
                    src = node_index.get(repo.team.team_name)
                    tgt = node_index.get(dep.team.team_name)
                    if src is not None and tgt is not None:
                        edges.append({'source': src, 'target': tgt})
        except Exception:
        
            pass

    context = {
        'nodes_json': json.dumps(nodes),
        'edges_json': json.dumps(edges),
        'node_count': len(nodes),
        'edge_count': len(edges),
        'page_title': 'Global Dependency Graph',
    }
    return render(request, 'organization/dependency_graph.html', context)
