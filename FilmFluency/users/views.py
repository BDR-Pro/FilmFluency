from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import UserProgress, LeaderboardEntry, UserProfile
from learning.models import Notification    
from django.contrib.auth.decorators import login_required
from learning.models import Movie , Video
from users.models import Report
import requests
from django.conf import settings
from learning.models import Language
from django.http import JsonResponse
from django_countries import countries
from django.shortcuts import get_object_or_404
from .forms import UserProfileForm
from django.contrib.contenttypes.models import ContentType

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            user = form.save()
            login(request, user)
            UserProgress.objects.create(user=user)  # Initialize progress tracking
            UserProfile.objects.create(user=user) # Initialize user profile
            return redirect('users:profile')  # Redirect to profile page after signup
    
        else:
            print(form.errors)
    
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

@login_required(login_url='users:login')
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


@login_required(login_url='users:login')
def edit_profile(request):
    middle_east_country_codes = {
        'SA', 'AE', 'KW', 'QA', 'OM', 'BH', 'IR', 
        'IQ', 'IL', 'JO', 'LB', 'SY', 'YE'
    }

    # Prepare a list of Middle Eastern countries
    middle_east_countries = [
        {'code': code, 'name': name} for code, name in countries if code in middle_east_country_codes
    ]

    # Prepare a list of other countries by excluding Middle Eastern countries
    other_countries = [
        {'code': code, 'name': name} for code, name in countries if code not in middle_east_country_codes
    ]
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    langs = Language.objects.all()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Profile updated successfully.'}, safe=False)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'edit_profile.html', {'form': form, 'profile': user_profile, 'languages': langs, 'middle_east_countries': middle_east_countries,
        'other_countries': other_countries })

@login_required(login_url='users:login')
def notify_me(request):
    if request.method == 'GET':
        slug = request.GET.get('movie')
        if Notification.objects.filter(recipient=request.user, movie=Movie.objects.get(random_slug=slug)).exists():
            Notification.objects.filter(recipient=request.user, movie=Movie.objects.get(random_slug=slug)).delete()
            return JsonResponse({'success': True, 'message': 'Notification removed successfully.'})
        Notification.objects.create(
            recipient=request.user,
            movie=Movie.objects.get(random_slug=slug),
            title = 'New video available',
            message = 'A new video is available for you to watch'
        )
        
        # Adjust your Django view to include a 'success' key in the JSON response
    return JsonResponse({'success': True, 'message': 'Report submitted successfully'})

@login_required(login_url='users:login')
def favorite(request):
    if request.method == 'GET':
        try:
            
            slug = request.GET.get('movie')
            movie = Movie.objects.get(random_slug=slug)
            user = UserProgress.objects.get(user=request.user)
            if user.favourite_movies.filter(random_slug=slug).exists():
                user.favourite_movies.remove(movie)
                user.save()
                return JsonResponse({'success': True, 'message': 'Movie removed from favorites successfully.'})
            user.favourite_movies.add(movie)
            user.save()
            return JsonResponse({'success': True, 'message': 'Movie added to favorites successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})



@login_required(login_url='users:login')
def report_item(request):
    if request.method == 'GET':
        model_type = request.GET.get('type')
        slug = request.GET.get('slug')
        if model_type == 'movie':
            item = get_object_or_404(Movie, random_slug=slug)
        elif model_type == 'video':
            item = get_object_or_404(Video, random_slug=slug)
        else:
            return JsonResponse({'message': 'Invalid type'}, status=400)
        
        if Report.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(item), object_id=item.id).exists():
            return JsonResponse({'message': 'You have already reported this item'}, status=400)
        
        report = Report.objects.create(
            user=request.user,
            content_object=item,
            report=request.GET.get('report', 'No reason provided')
        )
        report.save()
        return JsonResponse({'success': True, 'message': 'Report submitted successfully'})
    return JsonResponse({'message': 'Failed'}, status=400)

