from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserProgress, LeaderboardEntry, UserProfile
from learning.models import Notification    
from django.contrib.auth.decorators import login_required
from learning.models import Movie , Video
from users.models import Report
from learning.models import Language
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .forms import SignUpForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from .func import regex_email
from django_countries import countries


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')  # Access email data
            refferal = form.cleaned_data.get('referred_by')
            
            if not regex_email(email):
                return render(request, 'signup.html', {'form': form, 'error': 'Invalid email address (Do not use disposable emails)'})
            # Authenticate and log the user in
            user = authenticate(username=username, password=password, email=email)
            
            login(request, user)

            # Initialize user-related data
            UserProgress.objects.create(user=user)
            UserProfile.objects.get_or_create(user=user)
            if refferal:
                profile = UserProfile.objects.get(user=user)
                profile.credit += 7.5
                profile.referred_by = User.objects.get(referral_code=refferal)
                profile.save()
                referred_by = User.objects.get(referral_code=refferal)
                referred_by_profile = UserProfile.objects.get(user=referred_by)
                referred_by_profile.credit += 7.5
                referred_by_profile.save()
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            profile = UserProfile.objects.get(user=request.user)
            profile.cover_picture = 'https://filmfluency.fra1.digitaloceanspaces.com/covers/night.gif'
            profile.profile_picture = 'https://filmfluency.fra1.digitaloceanspaces.com/avatars/giphy.gif'
            profile.save()
            return redirect('users:profile')  # Redirect to profile page after signup
        else:
            print(form.errors)
    else:
        form = SignUpForm()
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
        
    if request.user.is_authenticated:
        return redirect('web:home')
    
    if request.method == 'GET':
        context = {
        'next': request.GET.get('next', '{% url "users:profile" %}')
    }
    return render(request, 'login.html', context)

@login_required(login_url='users:login')
def logout_view(request):
    logout(request)
    return redirect('web:home')


from django.db import models
from django.urls import reverse
from urllib.parse import urlencode

def profile(request):

    user = request.GET.get('user')
    if user == None:
        if request.user.is_anonymous:
            return redirect('users:login')
        base_url=reverse('users:profile')
        query_string = urlencode({'user': str(request.user)})
        url = f"{base_url}?{query_string}"
        return redirect(url)
    user = User.objects.get(username=user)
    user_progress, created = UserProgress.objects.get_or_create(user=user)
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    highest_complexity = Video.objects.order_by('-complexity').first()
    user_complexity_avg_complexity = user_progress.videos_watched.aggregate(models.Avg('complexity'))['complexity__avg']
    
    try:
        percntage_complexity = (user_complexity_avg_complexity / highest_complexity) * 100
    except:
        percntage_complexity = 0
        
    # If created, you can set default values or perform other initialization logic here
    if created:
        # For example, initializing some fields if necessary
        user_progress.points = 0
        user_progress.user_level = 1
        user_progress.save()
        
    
    user_profile = UserProfile.objects.get(user=user)

    
    return render(request, 'profile.html', {
        'user': request.user,
        'user_profile': user_profile,
        'user_progress': user_progress,
        'percntage_complexity': percntage_complexity,
    })
    
@login_required(login_url='users:login')
def follow_user(request):
        # Get or create UserProgress object for the logged-in user
    if request.method == 'POST':
        #follow user
        if request.POST.get('user') == request.user.username:
            return JsonResponse({'success': False, 'message': 'You cannot follow yourself.'})
        user = User.objects.get(username=request.POST.get('user'))
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_profile.friends.add(user)
        user_profile.save()
        return JsonResponse({'success': True, 'message': 'User followed successfully.'})
    return JsonResponse({'success': False, 'message': 'Use POST method to follow a user.'})

def leaderboard(request):
    entries = LeaderboardEntry.objects.all()[:10]  # Top 10 entries
    return render(request, 'leaderboard.html', {'entries': entries})


@login_required(login_url='users:login')
def edit_profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Manual handling of the form data
        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.country = request.POST.get('country', user_profile.country)
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        user_profile.save()
        return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})

    middle_east_codes = {'SA', 'AE', 'KW', 'QA', 'OM', 'BH', 'IR', 'IQ', 'IL', 'JO', 'LB', 'SY', 'YE'}
    middle_east_countries = [(code, name) for code, name in countries if code in middle_east_codes]
    other_countries = [(code, name) for code, name in countries if code not in middle_east_codes]

    context = {
        'user_profile': user_profile,
        'middle_east_countries': middle_east_countries,
        'other_countries': other_countries
    }
    return render(request, 'edit_profile.html', context)



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




def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        user.set_password('new_password')
        user.save()
        return render(request, 'password_reset.html') 
    return render(request, 'password_reset.html')