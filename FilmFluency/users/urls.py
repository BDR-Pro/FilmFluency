from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('notify-me/<str:slug>/', views.notify_me, name='notify_me'),
    path('add-to-favorites/<str:slug>>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove-from-favorites/<str:slug>>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('report/<str:slug>/', views.report_movie, name='report_movie'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]
