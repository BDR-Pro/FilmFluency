from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('notify-me/', views.notify_me, name='notify_me'),
    path('favorite/', views.favorite, name='favorite'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('report/', views.report_item, name='report'),
    path('change-password/', views.password_reset, name='password_reset'),
    path('follow/', views.follow_user, name='follow_user'),
    path('Money/', views.money, name='referral'),
]
