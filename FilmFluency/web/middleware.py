from django.http import HttpResponse

class BrowserCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the user agent from the request
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

        # Check if the user agent does not contain 'chrome' or 'edg'
        if 'chrome' not in user_agent and 'edg' not in user_agent:
            # Return an HTTP 403 Forbidden response
            return HttpResponse('Access denied: please use Chrome or Edge.', status=403)

        # Proceed with the normal flow if the condition is not met
        response = self.get_response(request)
        return response
