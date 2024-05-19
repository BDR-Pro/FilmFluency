from functools import wraps
from django.http import HttpResponse
from users.models import UserProfile

def check_paid_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:    #if the user is superuser, then they can access the api
            return view_func(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized", status=401)
        profile = UserProfile.objects.get(user=request.user) 
        if not profile.paid_user:
            return HttpResponse("Unauthorized", status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
