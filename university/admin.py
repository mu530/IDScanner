from django.contrib import admin
from .models import *
from django import forms
from django.forms.models import inlineformset_factory


# class UserRoleAdmin(admin.ModelAdmin):
#     list_display = ('user', 'is_registerar',  'is_cafe_staff',
#                     'is_security', 'is_proctore', 'is_librarist')
#     search_fields = ('user__first_name', 'user__last_name')
#     list_filter = ('REGISTRAR', 'LIBRARIAN',
#                    'SECURITY', 'PROCTOR', 'CAFE_STAFF')
#     list_select_related = ('user',)


@admin.register(DisciplinaryRecord)
class DisciplinaryRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'staff', 'date')
    search_fields = ('student__first_name', 'student__last_name',
                     'student__student_id', 'staff__first_name', 'staff__last_name')
    list_filter = ('student__first_name', 'student__last_name',
                   'student__student_id', 'staff__first_name', 'staff__last_name')


# Student registration and QR code generation module
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name',  'student_id')
    search_fields = ('first_name', 'last_name',  'student_id')
    exclude = ('student_id', 'qr_code')
    list_filter = ('department', 'department__field', 'registration_date', 'financial_aid',
                   'is_cafe_user', 'is_student_associative', 'is_active')
    list_per_page = 30
    ordering = ('last_name', 'first_name')


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'relationship',
                    'country', 'region', 'state', 'phone_number')
    search_fields = ('name', 'country', 'region', 'state')
    list_filter = ('country', 'region')


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_am', 'address')
    search_fields = ('name', 'name_am', 'address__email',
                     'address__country', 'address__region', 'address__state')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('telephone_phone', 'email',
                    'country', 'region', 'state')
    search_fields = ('email', 'country', 'region', 'state')
    list_filter = ('country', 'region')


admin.site.register(Field)
admin.site.register(Department)


# Cafeteria service module
@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('meal_period', 'start_date', 'end_date')
    search_fields = ('meal_period', 'start_date', 'end_date')
    list_filter = ('meal_period', 'start_date', 'end_date')


@admin.register(SpecialMealPeriod)
class SpecialMealPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_type', 'expiration_date')
    search_fields = ('coupon_type', 'discription')
    list_filter = ('coupon_type', 'expiration_date')


@admin.register(CafeAttendance)
class CafeAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'meal', 'check_in_time')
    search_fields = ('student__first_name', 'student__first_last',
                     'student__student_id', 'meal', 'meal__meal_period')
    list_filter = ('meal__meal_period', 'meal__start_date',
                   'meal__end_date', 'check_in_time')


# Library
@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'taken_date')
    search_fields = ('student__first_name', 'student__last_name',
                     'student__student_id', 'book__title', 'taken_date')
    list_filter = ('taken_date', )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn')
    search_fields = ('title', 'author', 'isbn')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('student', 'device_type', 'device_model',
                    'serial_number', 'date_added')
    search_fields = ('student', 'device_type', 'device_model', 'serial_number')
    list_filter = ('device_type', 'date_added')
