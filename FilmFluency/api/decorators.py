from functools import wraps
from django.http import HttpResponse

def check_paid_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_paid:
            return HttpResponse("Unauthorized", status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
