from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core import validators
import uuid
import qrcode
import datetime

from .utils import generate_qr_code
from .validators import *


def get_student_photo_filepath(self, image):
    return f"students/{self.full_name}/photo/{self.full_name}.png"


def get_default_photo():
    return "profile_images/default_profile_pic.png"


def get_student_qr_code_filepath(self, image):
    return f"student/{self.full_name}/qr_code/{self.full_name}.png"


def get_profile_image_filepath(self, image):
    return f"staffs/{self.username}/profile_images/{self.username}_profile_image.png"


def get_default_profile_image():
    return "profile_images/default_profile_pic.png"


class Staff(AbstractUser):
    ROLE = (
        ("REGISTRAR", "Registrar"),
        ("LIBRARIAN", "Librarian"),
        ("PROCTOR", "Proctor"),
        ("SECURITY", "Security"),
        ("CAFE_STAFF", "Cafe Staff"),
        ("ADMIN", "Admin"),
    )
    full_name_am = models.CharField(
        "ሙሉ ስም", max_length=200, validators=[validate_amharic], null=True, blank=True
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[validate_ethiopian_phone_number],
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        "profile picture",
        upload_to=get_profile_image_filepath,
        default=get_default_profile_image,
        blank=True,
    )
    email = models.EmailField("email address", unique=True, null=True, blank=True)
    role = models.CharField("Role", max_length=10, choices=ROLE)


    # def get_absolute_url(self):
    #     return reverse("staff_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.pk is None and self.is_superuser:
            self.role = "ADMIN"
        if self.role in ("ADMIN", "REGISTRAR"):
            self.is_superuser = True
        if self.role not in ("ADMIN", "REGISTRAR"):
            self.is_superuser = False
        if self.photo is None:
            self.photo = get_default_photo

        super().save(*args, **kwargs)


User = get_user_model()


class Address(models.Model):
    telephone_phone = models.CharField(max_length=20, validators=[
                                       validate_ethiopian_phone_number], null=True, blank=True)
    email = models.EmailField()
    country = models.CharField(max_length=150)
    region = models.CharField(max_length=150)
    state = models.CharField(max_length=150)

    def __str__(self):
        return self.country + ', ' + self.region + ', ' + self.state


class EmergencyContact(models.Model):
    name = models.CharField(max_length=255, verbose_name="Full Name")
    name_am = models.CharField(
        max_length=255, verbose_name="ሙሉ ስም", validators=[validate_amharic])
    relationship = models.CharField(
        max_length=255, verbose_name="relationship")
    relationship_am = models.CharField(
        max_length=255, verbose_name="ዝምድና", validators=[validate_amharic])
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    region = models.CharField(max_length=150, null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name

    def address(self):
        return self.country + ', ' + self.region + ', ' + self.state


class Coupon(models.Model):
    coupon_type = models.CharField(max_length=50)
    discription = models.TextField(max_length=100, null=True, blank=True)
    expiration_date = models.DateField(validators=[validators.MinValueValidator(
        limit_value=datetime.datetime.today().date(), message="Expiration date cannot be earlier than today's date.")])

    def __str__(self):
        return f"{self.coupon_type} - {self.expiration_date}"


class Campus(models.Model):
    name = models.CharField(max_length=255, verbose_name='Campus Name')
    name_am = models.CharField(
        max_length=255, verbose_name='የካምፓስ ስም', validators=[validate_amharic])
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Field(models.Model):
    name = models.CharField(max_length=255, verbose_name='Field Name')
    name_am = models.CharField(
        max_length=255, verbose_name='ፊልድ', validators=[validate_amharic])
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name='Department Name')
    name_am = models.CharField(
        max_length=255, verbose_name='የትምህርት ክፍል', validators=[validate_amharic])
    field = models.ForeignKey(Field, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    # Fields for student information
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    first_name_am = models.CharField(
        max_length=100, verbose_name='ስም', validators=[validate_amharic])
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    last_name_am = models.CharField(
        max_length=100, verbose_name='የአባት ስም', validators=[validate_amharic])
    student_id = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='photos/', default='img/p_pic.png')
    qr_code = models.ImageField(upload_to='qr_codes')
    date_of_birth = models.DateField(validators=[validate_birth_date])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    government_id_number = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    emergency = models.ForeignKey(
        EmergencyContact, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, default=None, null=True, blank=True)
    financial_aid = models.BooleanField()
    is_cafe_user = models.BooleanField(default=True)
    is_student_associative = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    coupon = models.ManyToManyField(
        Coupon, verbose_name="coupon", blank=True,  related_name='students')
    year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    def age(self):
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Generate unique student ID and QR code when student is registered
        if not self.pk:

            # Generate UUID
            unique_id = uuid.uuid4().hex[:5].upper()

            # Get 2 digites of year
            current_year = datetime.datetime.now().year
            last_two_digits = current_year % 100
            year = str(last_two_digits)[-2:]

            # Set student ID in the format "UoG/XXXXX/year"
            self.student_id = f"UoG|{unique_id}|{year}"

            if not self.qr_code:
                self.qr_code = generate_qr_code(self.student_id)
        super().save(*args, **kwargs)


class Device(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='devices')
    device_type = models.CharField(max_length=80)
    device_model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=17)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.serial_number} ({self.student})"


class SpecialMealPeriod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Meal(models.Model):
    MEAL_PERIODS = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        # Add special meal periods from the SpecialMealPeriod model
        *[(special_meal_period.name.lower(), special_meal_period.name.title()) for special_meal_period in SpecialMealPeriod.objects.all()]
    )

    meal_period = models.CharField(choices=MEAL_PERIODS, max_length=20)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.get_meal_period_display()} - From {self.start_date} to {self.end_date}'.format(self.start_date, self.end_date)

    def time(self):
        return f'From {self.start_date} to {self.end_date}'.format(self.start_date, self.end_date)


class CafeAttendance(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='cafeatendance_set')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    has_eaten = models.BooleanField(default=False)
    check_in_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.student} - {self.meal} - {self.has_eaten}'

    def save(self, *args, **kwargs):
        if self.has_eaten:
            self.check_in_time = datetime.datetime.now().time()
        super().save(*args, **kwargs)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)

    def __str__(self):
        return f'{self.title} - {self.author}'


class Library(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    taken_date = models.DateTimeField(auto_now_add=True)


class DisciplinaryRecord(models.Model):
    # Fields for disciplinary record information
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.reason} on {self.date.strftime('%Y-%m-%d')}"
