# myapp/middleware.py
from django.contrib.auth.decorators import login_required
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # if not request.user.is_authenticated:
        #     # Exempt the login page from @login_required
        #     if request.path == reverse('university:login'):
        #         return response
        #     if request.path == reverse('university:logout'):
        #         return response
        #     return login_required(lambda r: response)(request)

        return response
