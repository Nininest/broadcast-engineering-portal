from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Meeting


@login_required
def schedule_list(request):
    now = timezone.now()
    view_type = request.GET.get('view', 'upcoming')

    if view_type == 'weekly':
        meetings = Meeting.objects.filter(date_time__gte=now, date_time__lte=now + timedelta(weeks=1))
    elif view_type == 'monthly':
        meetings = Meeting.objects.filter(date_time__gte=now, date_time__lte=now + timedelta(days=30))
    else:
        meetings = Meeting.objects.filter(date_time__gte=now)

    return render(request, 'scheduling/schedule_list.html', {
        'meetings': meetings,
        'view_type': view_type,
    })


@login_required
def schedule_meeting(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        agenda = request.POST.get('agenda', '')
        platform = request.POST.get('platform')
        meeting_link = request.POST.get('meeting_link', '')
        date_time = request.POST.get('date_time')
        duration_minutes = request.POST.get('duration_minutes', 60)
        attendee_ids = request.POST.getlist('attendees')

        meeting = Meeting.objects.create(
            title=title,
            agenda=agenda,
            platform=platform,
            meeting_link=meeting_link,
            date_time=date_time,
            duration_minutes=duration_minutes,
            organizer=request.user,
        )
        meeting.attendees.set(attendee_ids)
        messages.success(request, 'Meeting scheduled successfully.')
        return redirect('scheduling:meeting_detail', pk=meeting.pk)

    from django.contrib.auth.models import User
    users = User.objects.all()
    platforms = Meeting.PLATFORM_CHOICES
    return render(request, 'scheduling/schedule_meeting.html', {
        'users': users,
        'platforms': platforms,
    })


@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'scheduling/meeting_detail.html', {'meeting': meeting})


@login_required
def delete_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, 'Meeting deleted.')
        return redirect('scheduling:schedule_list')
    return render(request, 'scheduling/meeting_detail.html', {'meeting': meeting})
