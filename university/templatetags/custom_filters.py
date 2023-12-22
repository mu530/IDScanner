from django import template
# from university.models import UserRole

register = template.Library()


@register.filter(name='has_user_role')
def has_user_role(user, role):
    """
    Checks if the given user has the specified role .
    Usage: {{ request.user|has_user_role:"is_cafe_staff" }}
    """

    return user.role == role