# middleware.py
from django.utils.deprecation import MiddlewareMixin

class CheckIframeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.is_iframe = 'iframe' in request.GET or request.headers.get('X-Frame-Mode') == 'iframe'
        return None


class CheckRefferalUrlMiddleware(MiddlewareMixin):
    def process_request(self, request):
        #check if the code of refferal in the url and set a cookie for the user to remember the refferal code 3 days
        if 'refferal' in request.GET:
            request.session['refferal'] = request.GET['refferal']
            request.session.set_expiry(259200)
        return None