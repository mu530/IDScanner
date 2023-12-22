from tkinter.tix import Form
from django import forms
from tinymce.widgets import TinyMCE
from django.forms.widgets import DateTimeInput
from django.contrib.auth.forms import UserCreationForm

from .models import *


Staff = get_user_model()


class StaffRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Staff
        fields = ("username", "email", "role", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(StaffRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "form-control"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "form-control"}
        )


class StaffChangeForm(forms.ModelForm):

    class Meta:
        model = Staff
        fields = (
            "username",
            "email",
            "role",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
            "photo",
        )



class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = '__all__'


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        exclude = ('address',)


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        exclude = ('student_id', 'qr_code', 'address', 'emergency')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'max': str(datetime.date.today() - datetime.timedelta(days=10*365))}),
        }


class CampusForm(forms.ModelForm):
    class Meta:
        model = Campus
        exclude = ('address', )


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = '__all__'


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        exclude = ('student', 'date_added')


class DisciplinaryRecordForm(forms.ModelForm):
    class Meta:
        model = DisciplinaryRecord
        fields = '__all__'


class DisciplinaryRecordForm(forms.ModelForm):
    reason = forms.CharField(widget=TinyMCE(
        attrs={'class': 'form-control tinymce', 'rows': 5}))

    class Meta:
        model = DisciplinaryRecord
        fields = ['reason',]


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': str(datetime.date.today())}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': str(datetime.date.today())}),
            'start_time': forms.DateInput(attrs={'type': 'time', 'min': str(datetime.date.today())}),
            'end_time': forms.DateInput(attrs={'type': 'time', 'min': str(datetime.date.today())}),

        }


class CafeAttendanceForm(forms.ModelForm):

    class Meta:
        model = CafeAttendance
        exclude = ('check_in_time', 'has_eaten', )


class SpecialMealPeriodForm(forms.ModelForm):
    class Meta:
        model = SpecialMealPeriod
        fields = '__all__'


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'expiration_date': DateTimeInput(attrs={'type': 'date', 'min': str(datetime.date.today())})
        }

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data['expiration_date']
        if expiration_date < datetime.datetime.today().date():
            raise ValidationError(
                "Expiration date cannot be earlier than today's date.")
        return expiration_date


class StudentCouponForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['coupons']

    coupons = forms.ModelMultipleChoiceField(
        queryset=Coupon.objects.all(), widget=forms.CheckboxSelectMultiple)
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['coupons'].required = True
        self.fields['students'].required = True


# Library module
class BookRentalForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Library
        fields = ('student', 'book')
        widgets = {
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
