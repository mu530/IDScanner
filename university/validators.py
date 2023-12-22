from django.core.exceptions import ValidationError
import regex as re
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def validate_birth_date(birth_date):
    age = timezone.now().date() - birth_date
    if age.days < 16 * 365:
        raise ValidationError(
            _('You must be at least 16 years old to register'), code='small_age')


def validate_amharic(value):
    if not re.match(r'^[\p{Ethiopic}\s]+$', value):
        raise ValidationError(
            _('Only Amharic characters are allowed.'),
            code='invalid_amharic'
        )


def validate_ethiopian_phone_number(value):
    # Remove any whitespace or dashes from the input
    cleaned_value = re.sub(r'\s+|-', '', value)

    # Check that the input contains only digits
    if not cleaned_value.isdigit():
        raise ValidationError(
            _('Phone number can only contain digits.'),
            code='invalid_phone_number'
        )

    # Check that the input is a valid Ethiopian phone number
    if not re.match(r'^[79][0-9]{8}$', cleaned_value):
        raise ValidationError(
            _('Invalid Ethiopian phone number.'),
            code='invalid_phone_number'
        )


# def validate_phone_number(value):
#     cleaned_value = value.strip().replace('-', '').replace(' ', '')
#     try:
#         validate_ethiopian_phone_number(cleaned_value)
#     except ValidationError as e:
#         raise ValidationError(
#             _('Invalid phone number: %(value)s'),
#             code='invalid_phone_number',
#             params={'value': value},
#         )
