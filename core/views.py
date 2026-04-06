from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from .models import Department, Team, UserProfile, AuditLog
from .forms import RegisterForm, ProfileUpdateForm, PasswordChangeForm

def login_view(request):
    if request.user.is_authenticated: 
        return redirect('dashboard')
    if request.method == 'POST': 
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user: 
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')

def register_view(request): 
    if request.user.is_authenticated: 
        return redirect('dashboard')
    if request.method == 'POST': 
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            dept_id = request.POST.get('department')
            profile = UserProfile(user=user, role=form.cleaned_data.get('role', ''))
            if dept_id: 
                try:
                    profile.department = Department.objects.get(pk=dept_id)
                except Department.DoesNotExist: 
                    pass
            profile.save()
            login(request, user)
            messages.success(request, 'Account Created Successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    departments = Department.objects.all()
    return render(request, 'core/register.html', {'form':form, 'departments':departments})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    total_teams = Team.objects.count()
    active_teams = Team.objects.filter(status = 'active').count()
    total_departments = Department.objects.count()
    total_engineers = User.objects.count()
    recent_teams = Team.objects.order_by(' -updated at')[:5]
    recent_logs = AuditLog.objects.order_by(' -timestamp')[:5]
    context = {
        'total_teams': total_teams, 
        'active_teams' : active_teams, 
        'total_departments': total_departments, 
        'total_engineers': total_engineers, 
        'recent_teams': recent_teams, 
        'recent_logs': recent_logs,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile_view(request): 
    profile, _ = UserProfile.objects.get_or_create(user= request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance= request.user)
        if form.is_valid():
            form.save()
            profile.role = request.POST.get('role', '')
            dept_id = request.POST.get('department')
            if dept_id: 
                try:
                    profile.department = Department.objects.get(pk= dept_id)
                except Department.DoesNotExist: 
                    pass
            profile.save()
            messages.success(request, 'Profile Updated Successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance= request.user)
    departments = Department.objects.all()
    return render(request, 'core/profile.html', {
        'form': form, 
        'departments': departments
    })

@login_required
def change_password_view(request): 
    if request.method == 'POST': 
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password Changed Successfully!')
            return redirect('profile')
    else: 
        form  = PasswordChangeForm(request.user)
    return render(request, 'core/change_password.html', {
        'form': form
    })
