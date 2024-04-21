from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import UserProgress, LeaderboardEntry, UserProfile
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            UserProgress.objects.create(user=user)  # Initialize progress tracking
            return redirect('users:profile')  # Redirect to profile page after signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('web:home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('web:home')



@login_required(login_url='users:login')
def profile(request):
    # Get or create UserProgress object for the logged-in user
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)
    user_progress, created = UserProfile.objects.get_or_create(user=request.user)

    
    # If created, you can set default values or perform other initialization logic here
    if created:
        # For example, initializing some fields if necessary
        user_progress.points = 0
        user_progress.user_level = 1
        user_progress.save()

    return render(request, 'profile.html', {
        'user': request.user,
        'progress': user_progress
    })

def leaderboard(request):
    entries = LeaderboardEntry.objects.all()[:10]  # Top 10 entries
    return render(request, 'leaderboard.html', {'entries': entries})

def edit_profile(request):
    pass



def notify_me(request, slug):
    pass

def add_to_favorites(request, slug):
    pass

def remove_from_favorites(request, slug):
    
    pass


def report_movie(request, slug):
    pass

    