from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse

from .models import Team, TeamMember, TeamSkill
from .forms import EmailTeamForm, ScheduleMeetingForm


@login_required
def team_list(request):
    query = request.GET.get('q', '').strip()
    teams = (
        Team.objects
        .filter(is_active=True)
        .select_related('manager')
        .prefetch_related('members', 'skills')
        .order_by('name')
    )
    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(mission__icontains=query) |
            Q(department_name__icontains=query) |
            Q(manager__first_name__icontains=query) |
            Q(manager__last_name__icontains=query) |
            Q(manager__username__icontains=query) |
            Q(email__icontains=query)
        )
    context = {'teams': teams, 'query': query, 'total_count': teams.count()}
    return render(request, 'teams/team_list.html', context)


@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk, is_active=True)
    members    = team.members.select_related('user').order_by('role', 'user__username')
    skills     = team.skills.all()
    upstream   = team.upstream_dependencies.filter(is_active=True).select_related('manager')
    downstream = team.downstream_dependents.filter(is_active=True).select_related('manager')
    context = {
        'team': team, 'members': members,
        'skills': skills, 'upstream': upstream, 'downstream': downstream,
    }
    return render(request, 'teams/team_detail.html', context)


@login_required
def email_team(request, pk):
    team = get_object_or_404(Team, pk=pk, is_active=True)
    if not team.email:
        messages.warning(request, f'"{team.name}" does not have a contact email address configured.')
        return redirect('teams:team_detail', pk=pk)
    if request.method == 'POST':
        form = EmailTeamForm(request.POST)
        if form.is_valid():
            subject     = form.cleaned_data['subject']
            body        = form.cleaned_data['body']
            sender_name = request.user.get_full_name() or request.user.username
            sender_email = request.user.email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            full_message = (
                f"Message sent via Broadcast Engineering Portal\n"
                f"From: {sender_name} ({sender_email})\n"
                f"{'─' * 50}\n\n{body}"
            )
            try:
                send_mail(
                    subject=f"[Broadcast Portal] {subject}",
                    message=full_message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                    recipient_list=[team.email],
                    fail_silently=False,
                )
                messages.success(request, f'Your message has been sent to {team.name} at {team.email}.')
                return redirect('teams:team_detail', pk=pk)
            except Exception as exc:
                messages.error(request, f'Failed to send email: {exc}')
    else:
        form = EmailTeamForm()
    return render(request, 'teams/email_team.html', {'team': team, 'form': form})


@login_required
def schedule_meeting(request, pk):
    """Schedule a meeting with a specific team."""
    team = get_object_or_404(Team, pk=pk, is_active=True)
    if request.method == 'POST':
        form = ScheduleMeetingForm(request.POST)
        if form.is_valid():
            meeting_date     = form.cleaned_data['meeting_date']
            meeting_time     = form.cleaned_data['meeting_time']
            platform         = form.cleaned_data['platform']
            duration_minutes = form.cleaned_data['duration_minutes']
            agenda           = form.cleaned_data['agenda']
            organiser_name   = request.user.get_full_name() or request.user.username
            organiser_email  = request.user.email or 'N/A'
            meeting_dt = f"{meeting_date.strftime('%A, %d %B %Y')} at {meeting_time.strftime('%H:%M')}"
            if team.email:
                body = (
                    f"Meeting Request via Broadcast Engineering Portal\n"
                    f"{'─' * 50}\n"
                    f"Team:       {team.name}\n"
                    f"Organiser:  {organiser_name} ({organiser_email})\n"
                    f"Date/Time:  {meeting_dt}\n"
                    f"Duration:   {duration_minutes} minutes\n"
                    f"Platform:   {platform}\n"
                    f"{'─' * 50}\n\nAgenda / Notes:\n{agenda}"
                )
                try:
                    send_mail(
                        subject=f"[Meeting Request] {organiser_name} -> {team.name}",
                        message=body,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                        recipient_list=[team.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
            messages.success(
                request,
                f'Meeting with {team.name} scheduled for {meeting_dt} via {platform}.'
            )
            return redirect('teams:team_detail', pk=pk)
    else:
        form = ScheduleMeetingForm()
    return render(request, 'teams/schedule_meeting.html', {'team': team, 'form': form})


@login_required
def team_dependencies(request, pk):
    team = get_object_or_404(Team, pk=pk, is_active=True)
    upstream   = team.upstream_dependencies.filter(is_active=True).select_related('manager')
    downstream = team.downstream_dependents.filter(is_active=True).select_related('manager')
    nodes = [{'id': team.pk, 'label': team.name, 'group': 'focus'}]
    edges = []
    for t in upstream:
        nodes.append({'id': t.pk, 'label': t.name, 'group': 'upstream'})
        edges.append({'from': t.pk, 'to': team.pk})
    for t in downstream:
        nodes.append({'id': t.pk, 'label': t.name, 'group': 'downstream'})
        edges.append({'from': team.pk, 'to': t.pk})
    context = {
        'team': team, 'upstream': upstream, 'downstream': downstream,
        'graph_nodes': nodes, 'graph_edges': edges,
    }
    return render(request, 'teams/dependencies.html', context)


@login_required
def team_search_api(request):
    q = request.GET.get('q', '').strip()
    teams = Team.objects.filter(is_active=True)
    if q:
        teams = teams.filter(Q(name__icontains=q) | Q(department_name__icontains=q))
    data = [
        {
            'id': t.pk, 'name': t.name,
            'department': t.department_name,
            'manager': (t.manager.get_full_name() or t.manager.username if t.manager else None),
            'email': t.email,
            'slack_channel': t.slack_channel,
        }
        for t in teams[:20]
    ]
    return JsonResponse({'results': data})
