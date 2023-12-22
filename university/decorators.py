from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404


def role_required(role_names):
    def check_role(user):
        if user.is_superuser or user.is_staff:
            return True

        # user_roles = user.objects.filter(
        #     user=user, **{f"{name}": True for name in role_names}
        # ).exists()

        return user.role == role_names

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not check_role(request.user):
                raise Http404
            return view_func(request, *args, **kwargs)
        return wrapper

    return decorator
