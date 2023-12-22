from .models import Student, Department
from django.shortcuts import render
from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View, CreateView, ListView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.db.models.functions import Trunc
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView

from .models import *
from .forms import *
from .decorators import role_required


def paginate(request, data, per_page=10):
    paginator = Paginator(data, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    context = {
        'title': 'Welcome to University of Gondar!',
        'subtitle': 'Learn more about our services',
        'services': [
            {'title': 'Undergraduate Programs',
                'description': 'We offer a wide range of undergraduate programs in various fields of study, including: Accounting, Agriculture, Architecture, Business Administration, Civil Engineering, Computer Science, Education, Environmental Science, Law, Medicine, Nursing, Pharmacy, Public Health, and more.'},
            {'title': 'Graduate Programs',
                'description': 'We offer several graduate programs, including master\'s and doctoral degrees in various fields of study, including: Accounting, Agriculture, Architecture, Business Administration, Civil Engineering, Computer Science, Education, Environmental Science, Law, Medicine, Nursing, Pharmacy, Public Health, and more.'},
            {'title': 'Research',
                'description': 'We conduct research in various areas, including health, agriculture, technology, social sciences, and humanities.'},
            {'title': 'Community Engagement',
                'description': 'We work closely with local communities to address social and economic challenges, including health, education, and poverty reduction.'},
            {'title': 'Continuing Education',
                'description': 'We offer continuing education programs and professional development courses for working professionals and lifelong learners.'},
            {'title': 'International Programs',
                'description': 'We offer international programs and exchange opportunities for students and faculty to study and collaborate with partner institutions around the world.'},
        ],
        'contact': {
            'email': 'info@example.com',
            'phone': '+1 (555) 123-4567',
            'address': '123 Main St, Anytown USA',
        },
        'university': {
            'name': 'University of Gondar',
            'location': 'Gondar, Ethiopia',
            'description': 'The University of Gondar is a public research university located in the historic city of Gondar in Ethiopia. It was established in 1954 and has since grown into one of the largest and most prestigious universities in the country.',
            'photo': 'https://example.com/university-of-gondar.jpg',
        },
    }
    return render(request, 'index.html', context)


def about_us(request):
    return render(request, 'base/about.html')

# Staff
@login_required
@role_required(['REGISTRAR'])
def create_staff(request):

    
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # Handle successful form submission
            return redirect('university:home')
    else:
        form = StaffRegistrationForm()

    return render(request, 'university/staff/staff_register.html', {'form': form})


def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, username +
                             ' Welcome To UoG Student ID management System')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                if user.is_superuser:
                    return redirect('university:list-students')
                if user.role == 'CAFE_STAFF':
                    return redirect('university:cafe-manager')
                if user.role in ('SECURITY','PROCTOR'):
                    return redirect('university:disciplin-student-list')
                if user.role == 'LIBRARIAN':
                    return redirect('university:library-manager')
            return redirect('university:list-students')

        else:
            messages.error(request, 'username or password is incorrect')

    return render(request, 'university/login.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('university:login')

def staff_update(request, user_id):
    staff = get_object_or_404(Staff, pk=user_id)
    form = StaffChangeForm(instance=staff)

    if request.method == "POST":
        form = StaffChangeForm(request.POST, instance=staff)

        if form.is_valid():
            user = form.save()
            messages.success(request, (f"Profile updated for {user.username}"))
            return redirect("Staff:staff_detail", user.id)
        else:
            messages.error(request, ("please fix the errors"))

    context = {"form": form, "staff": staff}

    return render(request, "staff/update_profile.html", context)


class ChangePasswordView(PasswordChangeView):
    success_url = reverse_lazy('password_change_done')
    template_name = 'university/staff/change_password.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

@login_required
def view_card(request, student_id):

    context = {
        'student': Student.objects.get(student_id=student_id),
        'current_url': request.build_absolute_uri(),
    }

    return render(request, 'university/view_id.html', context)


@login_required
def view_scan(request):
    if request.method == 'GET':
        student_id = request.GET.get('student_id')
    if student_id is None:
        return HttpResponse("Student ID is Invalid")
    else:
        student_id = student_id.strip()
        context = {
            'student': Student.objects.get(student_id=student_id),
            'current_url': request.build_absolute_uri(),
        }

        return render(request, 'university/view_id.html', context)


# Student registration and QR code generation module
@login_required
@role_required(['REGISTRAR'])
def student_form(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)

        emergency_form = EmergencyContactForm(request.POST)

        student_form = StudentForm(request.POST, request.FILES)

        if address_form.is_valid() and student_form.is_valid() and emergency_form.is_valid():
            address = address_form.save()

            emergency = emergency_form.save()
            student = student_form.save(commit=False)
            student.address = address
            student.emergency = emergency
            student.save()

            return redirect('university:list-students')
    else:
        address_form = AddressForm()

        emergency_form = EmergencyContactForm()

        student_form = StudentForm()

    context = {
        'address_form': address_form,
        'student_form': student_form,
        'emergency_form': emergency_form,
        'action': 'Register',

        'current_url': request.build_absolute_uri(),
    }

    return render(request, 'university/student_form.html', context)


@login_required
@role_required(['REGISTRAR'])
def add_device(request, student_id):
    # Get the student object based on the id passed in the URL
    student = Student.objects.get(id=student_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Create a DeviceForm instance with the POST data
        form = DeviceForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Create a new device object with the student and form data
            device = form.save(commit=False)
            device.student = student
            device.save()

            # Redirect the user to the student detail page
            return redirect('university:student-profile', student_id=student.student_id)

    # If the request method is not POST, create an empty DeviceForm instance
    else:
        form = DeviceForm()

    # Render the add device form template with the DeviceForm instance and student object
    return render(request, 'university/registerar/add_device.html', {'form': form, 'student': student})


@login_required
@role_required(['REGISTRAR'])
def student_profile(request, student_id):
    student = Student.objects.get(student_id=student_id)
    address = Student.address
    emergency = Student.emergency
    library = Library.objects.filter(student=student)

    devices = student.devices.all()
    disciplinary_records = DisciplinaryRecord.objects.filter(student=student)

    # Get the search query from the request GET parameters
    search_query = request.GET.get('q')
    if search_query:
        disciplinary_records = disciplinary_records.filter(
            reason__icontains=search_query)

    # Paginate the disciplinary records
    page_number = request.GET.get('page')
    disciplinary_records = paginate(request, disciplinary_records, 5)

    if student.is_cafe_user:
        cafe = CafeAttendance.objects.filter(student=student)

    context = {
        'student': student,
        'devices': devices,
        'address': address,
        'emergency': emergency,
        'disciplinary_records': disciplinary_records,
        'current_url': request.build_absolute_uri(),
        'search_query': search_query,  # Pass the search query to the template
    }

    return render(request, 'university/student_profile.html', context)


@login_required
@role_required(['REGISTRAR'])
def update_student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    if request.method == 'POST':
        student_form = StudentForm(
            request.POST, request.FILES, instance=student)
        address_form = AddressForm(request.POST, instance=student.address)
        emergency_form = EmergencyContactForm(
            request.POST, instance=student.emergency)
        if student_form.is_valid() and address_form.is_valid():
            address_form.save()
            student_form.save()
            # Handle successful form submission
            return redirect('university:list-students')
    else:
        student_form = StudentForm(instance=student)
        address_form = AddressForm(instance=student.address)
        emergency_form = EmergencyContactForm(instance=student.emergency)

    context = {
        'address_form': address_form,
        'student_form': student_form,
        'emergency_form': emergency_form,
        'action': 'Update',
        'current_url': request.build_absolute_uri(),
    }

    return render(request, 'university/student_form.html', context)


@login_required
@role_required(['REGISTRAR'])
def students_list(request):
    # Get query parameters
    department_id = request.GET.get('department')
    year = request.GET.get('year')
    search_query = request.GET.get('search_query')
    sort_by = request.GET.get('sort_by', '-registration_date')

    # Get departments and selected department
    departments = Department.objects.all()
    selected_department = None
    if department_id:
        selected_department = Department.objects.get(id=department_id)

    # Filter students by selected department and year
    students = Student.objects.all()
    if selected_department:
        students = students.filter(department=selected_department)
    if year:
        students = students.filter(registration_date__year=int(year))

    # Search students by name or ID
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Sort students by selected field
    if sort_by == 'name':
        students = students.annotate(full_name=Concat(
            'first_name', Value(' '), 'last_name', output_field=models.CharField()))
        students = students.order_by('full_name')
    elif sort_by == 'department':
        students = students.order_by('department__name')
    elif sort_by == 'year':
        students = students.order_by('year')
    elif sort_by == 'gender':
        students = students.order_by('gender')
    else:
        students = students.order_by('-registration_date')

    # Count number of male and female students
    number_of_students = students.count()
    number_of_male_students = students.filter(gender='M').count()
    number_of_female_students = students.filter(gender='F').count()

    # Paginate students
    students = paginate(request, students)

    context = {
        'students': students,
        'page': 'Students_list',
        'page_title': 'Students',
        'numberOfStudents': number_of_students,
        'numberOfMaleStudents': number_of_male_students,
        'numberOfFemaleStudents': number_of_female_students,
        'current_url': request.build_absolute_uri(),
        'departments': departments,
        'selected_department': selected_department,
        'year': int(year) if year else None,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'university/students_list.html', context)


@login_required
@role_required(['REGISTRAR'])
def university_form(request):

    campus_form = CampusForm()
    field_form = FieldForm()
    department_form = DepartmentForm()
    address_form = AddressForm()

    if request.method == 'POST':
        if 'campus_submit' in request.POST:
            campus_form = CampusForm(request.POST or None)
            address_form = AddressForm(request.POST)
            if campus_form.is_valid() and address_form.is_valid():
                address = address_form.save()
                campus = campus_form.save(commit=False)
                campus.address = address
                campus.save()
                messages.success(request, f'{ campus.name } campus is Added')
                return redirect(request.path_info)

        if 'field_submit' in request.POST:
            field_form = FieldForm(request.POST)
            if field_form.is_valid():
                field = field_form.save()
                messages.success(request, f'{ field.name } field is Added')
                return redirect(request.path_info)

        if 'department_submit' in request.POST:
            department_form = DepartmentForm(request.POST or None)
            if department_form.is_valid():
                department = department_form.save()
                messages.success(
                    request, f'{ department.name } department is Added')
                return redirect(request.path_info)

    context = {
        'department_form': department_form,
        'campus_form': campus_form,
        'field_form': field_form,
        'address_form': address_form,

        'current_url': request.build_absolute_uri(),
    }

    return render(request, 'university/registerar/create.html', context)


@login_required
@role_required(['REGISTRAR'])
def department_list(request):
    departments = Department.objects.all().select_related('field__campus')

    # Filter data based on search query
    query = request.GET.get('q')
    if query:
        departments = departments.filter(name__icontains=query)

    # Filter data based on campus and field
    campus_id = request.GET.get('campus')
    field_id = request.GET.get('field')
    if campus_id:
        departments = departments.filter(field__campus__id=campus_id)
    if field_id:
        departments = departments.filter(field__id=field_id)

    # Pagination
    departments = paginate(request, departments)

    # Get all campuses and fields for filtering
    campuses = Campus.objects.all()
    fields = Field.objects.all()

    # Check if any filter or search is applied
    is_filtered = campus_id or field_id or query

    context = {
        'departments': departments,
        'campuses': campuses,
        'fields': fields,
        'selected_campus': int(campus_id) if campus_id else None,
        'selected_field': int(field_id) if field_id else None,
        'search_key': query,
        'is_filtered': is_filtered,
    }

    return render(request, 'university/registerar/department_list.html', context)


# Cafeteria service module
@login_required
@role_required(['CAFE_STAFF'])
def cafe_maneger(request):

    current_time = timezone.localtime(timezone.now())
    query = request.GET.get('query')
    meal_time = request.GET.get('meal_time')
    meal_periods = Meal.objects.all().values('meal_period')
    coupons = Coupon.objects.all()

    if meal_time:
        if meal_time != 'all':
            cafe_services = CafeAttendance.objects.filter(
                meal__meal_period=meal_time).order_by('has_eaten').select_related('student', 'meal')
        else:
            cafe_services = CafeAttendance.objects.all().order_by(
                'has_eaten').select_related('student', 'meal')
    else:
        cafe_services = CafeAttendance.objects.filter(
            Q(meal__start_time__lte=current_time + timezone.timedelta(minutes=60)) &
            Q(meal__end_time__gte=current_time - timezone.timedelta(minutes=60))
        ).order_by('has_eaten').select_related('student', 'meal')

    if query:
        cafe_services = cafe_services.filter(
            student__first_name__icontains=query) | CafeAttendance.objects.filter(
            student__last_name__icontains=query) | CafeAttendance.objects.filter(
            student__student_id__icontains=query).order_by(
            'has_eaten')

    num_students_did_not_eat = cafe_services.filter(
        has_eaten=False).values('student').distinct().count()
    num_students_did_eat = cafe_services.filter(
        has_eaten=True).values('student').distinct().count()
    cafe_users = Student.objects.filter(is_cafe_user=True)
    num_cafe_users = cafe_users.count()

    students_with_special_coupon = Student.objects.filter(
        coupon__coupon_type='special')
    num_special_users = students_with_special_coupon.count()

    meal = CafeAttendance.objects.filter(meal__start_date__lte=current_time.date(), meal__end_date__gte=current_time.date(
    ), meal__start_time__lte=current_time.time(), meal__end_time__gte=current_time.time()).annotate(
        num_eat=Count('has_eaten', filter=Q(
            has_eaten=True)),
        num_not_eat=Count('has_eaten', filter=Q(
            has_eaten=False))
    )

    cafe_services = paginate(request, cafe_services, 20)

    context = {
        'cafe_services': cafe_services,
        'cafe_users': cafe_users,
        'special_users': students_with_special_coupon,
        'meal': meal,
        'meal_periods': meal_periods,
        'meal_time': meal_time,
        'coupons': coupons,

        'num_cafe_users': num_cafe_users,
        'num_special_users': num_special_users,
        'num_students_did_not_eat': num_students_did_not_eat,
        'num_students_did_eat': num_students_did_eat,
        'current_url': request.build_absolute_uri(),


    }
    return render(request, 'university/cafe/admin.html', context)


@login_required
@role_required(['CAFE_STAFF'])
def eat_meal(request, pk):

    cafe_attendance_id = pk

    try:
        cafe_attendance = CafeAttendance.objects.get(id=cafe_attendance_id)
        if cafe_attendance.has_eaten:
            messages.error(
                request, f'{ cafe_attendance.student } have already attended {cafe_attendance.meal.meal_period} today.')
            return redirect('university:cafe-manger')
        cafe_attendance.has_eaten = True
        cafe_attendance.save()

        return redirect('university:cafe-manger')

    except CafeAttendance.DoesNotExist:

        messages.error(request, 'Invalid ID')

        return redirect('university:cafe-manger')


@login_required
@role_required(['CAFE_STAFF'])
def cafe_form(request):

    meal_period_form = SpecialMealPeriodForm()
    cafe_attendance_form = CafeAttendanceForm()
    meal_form = MealForm()

    if request.method == 'POST':
        if 'meal_period_submit' in request.POST:
            meal_period_form = SpecialMealPeriodForm(request.POST or None)
            if meal_period_form.is_valid():
                meal_period_form.save()
                messages.success(request, 'New Meal Period is Added')
                meal_period_form = SpecialMealPeriodForm()

        if 'cafe_attendance_submit' in request.POST:
            cafe_attendance_form = CafeAttendanceForm(request.POST)
            if cafe_attendance_form.is_valid():
                cafe_attendance_form.save()
                messages.success(request, 'New Meal Service is Added')
                cafe_attendance_form = CafeAttendanceForm()

        if 'meal_submit' in request.POST:
            meal_form = MealForm(request.POST or None)
            if meal_form.is_valid():
                meal_form.save()
                messages.success(request, 'New Meal Service Periods is Added')
                meal_form = MealForm()

    context = {
        'meal_form': meal_form,
        'meal_period_form': meal_period_form,
        'cafe_attendance_form': cafe_attendance_form,

        'current_url': request.build_absolute_uri(),
    }

    return render(request, 'university/cafe/form.html', context)


@login_required
@role_required(['CAFE_STAFF'])
def add_coupon(request):
    if request.method == 'POST':
        coupon_form = CouponForm(request.POST)

        if coupon_form.is_valid():
            coupon = coupon_form.save()

            return redirect('university:coupon-detail', coupon_id=coupon.id)
    else:
        coupon_form = CouponForm()

    context = {
        'coupon_form': coupon_form,
    }

    return render(request, 'university/cafe/add_coupon.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(['CAFE_STAFF']), name='dispatch')
class CouponListView(ListView):
    model = Coupon
    template_name = 'university/cafe/coupon_list.html'
    context_object_name = 'coupons'
    paginate_by = 10


@login_required
@role_required(['CAFE_STAFF'])
def coupon_detail(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    students = coupon.students.all()
    return render(request, 'university/cafe/coupon_detail.html', {'coupon': coupon, 'students': students})


@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(['CAFE_STAFF']), name='dispatch')
class CouponDeleteView(View):
    template_name = 'university/cafe/coupon_delete.html'

    def get(self, request, coupon_id):
        # Retrieve the coupon object or return a 404 error
        coupon = get_object_or_404(Coupon, id=coupon_id)

        # Get the list of students who have this coupon
        students = coupon.students.all()

        # Get the next page URL from the query string
        next_page = request.GET.get('next')

        # Render the template with the list of students and the next page URL
        context = {
            'coupon': coupon,
            'students': students,
            'next_page': next_page
        }
        return render(request, self.template_name, context)

    def post(self, request, coupon_id):
        # Retrieve the coupon object or return a 404 error
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon_type = coupon.coupon_type
        # Delete the coupon object
        coupon.delete()

        messages.success(
            request, f'{coupon_type} coupon was deleted successfully.')

        # Redirect to the next page if it is set; otherwise, redirect to the success page
        next_page = request.POST.get('next')
        if next_page:
            return redirect(next_page)

        else:
            return redirect('university:cafe-manager')

        # Redirect to the success page
        return redirect('university:success-page')


@login_required
@role_required(['CAFE_STAFF'])
def add_coupon_to_students(request):
    coupons = Coupon.objects.all()
    students = Student.objects.all()

    coupon_form = CouponForm(request.POST or None)
    student_coupon_form = StudentCouponForm(request.POST or None)

    if request.method == 'POST' and ("coupon_submit" in request.POST):
        if ("coupon_submit" in request.POST) and coupon_form.is_valid():
            coupon_form.save()
            messages.success(request, 'Coupon saved successfully.')
    if request.method == 'POST' and ("student_coupon_submit" in request.POST):
        if student_coupon_form.is_valid():
            selected_students = student_coupon_form.cleaned_data['students']
            selected_coupons = student_coupon_form.cleaned_data['coupons']
            for student in selected_students:
                student.coupons.add(*selected_coupons)
            messages.success(
                request, 'Coupon applied successfully to selected students.')

    return render(request, 'university/cafe/add_coupon_to_students.html', {
        'coupon_form': coupon_form,
        'student_coupon_form': student_coupon_form,
        'coupons': coupons,
        'students': students,
    })


@login_required
@role_required(['CAFE_STAFF'])
def cafe_user_detail(request, student_id):

    # Retrieve the student object
    student = get_object_or_404(Student, student_id=student_id)

    # Retrieve the CafeAttendance objects for the student, grouped by date
    attendance_data = CafeAttendance.objects.filter(student=student)\
        .annotate(hour=Trunc('check_in_time', 'hour'))\
        .values('hour')\
        .annotate(total=Count('id'))

    # Convert the query set into a list of dates and attendance counts
    dates = [a['hour'] for a in attendance_data]
    attendance_counts = [a['total'] for a in attendance_data]
    cafe_displines = DisciplinaryRecord.objects.filter(
        Q(staff__userrole__is_cafe_staff=True)
    )

    context = {
        'student': student,
        'dates': json.dumps(dates, cls=DjangoJSONEncoder),
        'attendance_counts': json.dumps(attendance_counts, cls=DjangoJSONEncoder),
        'cafe_displines': cafe_displines,
    }
    # Render the template with the attendance data
    return render(request, 'university/cafe/cafe_user_detail.html', context)


# Library Module
@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(['LIBRARIAN']), name='dispatch')
class LibraryListView(ListView):
    model = Library
    template_name = 'university/library/admin.html'
    context_object_name = 'libraries'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('search')
        sort_by = self.request.GET.get('sort')
        sort_dir = self.request.GET.get('dir', 'asc')
        qs = Library.objects.all()
        if query:
            qs = qs.filter(
                Q(student__first_name__icontains=query) |
                Q(student__last_name__icontains=query) |
                Q(student__id__icontains=query) |
                Q(book__title__icontains=query) |
                Q(book__author__icontains=query) |
                Q(book__isbn__icontains=query)
            )
        if sort_by:
            qs = qs.order_by(f'{sort_by}{"-" if sort_dir == "desc" else ""}')
        return qs


@login_required
@role_required(['LIBRARIAN'])
def library_student_list(request):
    query = request.GET.get('q')
    if query:
        students = Student.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(student_id__icontains=query)
        )
    else:
        students = Student.objects.all()
    return render(request, 'university/library/student_list.html', {'students': students})


@login_required
@role_required(['LIBRARIAN'])
def book_rental(request, student_id):
    student = Student.objects.get(student_id=student_id)
    # You can redirect to the book rental page with the selected student object
    return redirect('university:book-rental-page', student_id=student_id)


@login_required
@role_required(['LIBRARIAN'])
def book_rental_page(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(isbn__icontains=query)
        )
    else:
        books = Book.objects.all()
    context = {'student': student, 'books': books}
    return render(request, 'university/library/book_rental.html', context)


@login_required
@role_required(['LIBRARIAN'])
def rent_book(request, student_id, book_id):
    student = get_object_or_404(Student, student_id=student_id)
    book = get_object_or_404(Book, id=book_id)
    Library.objects.create(student=student, book=book)
    return redirect('university:library-manager')


@login_required
@role_required(['LIBRARIAN'])
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('university:library-manager')
    else:
        form = BookForm()
    return render(request, 'university/library/form.html', {'form': form})


@login_required
@role_required(['LIBRARIAN'])
def book_return(request, pk):
    library = get_object_or_404(Library, pk=pk)
    library.delete()
    return redirect('university:library-manager')


# Disciplinary recording module
@method_decorator(login_required, name='dispatch')
@role_required(['REGISTRAR', 'CAFE_STAFF', 'SECURITY', 'PROCTOR', 'LIBRARIAN'])
def add_disciplinary_record(request, student_id):

    current_url = request.build_absolute_uri()
    form = DisciplinaryRecordForm
    student = Student.objects.get(student_id=student_id)
    staff = request.user
    next_page = request.GET.get('next_page')

    if request.method == 'POST':
        form = DisciplinaryRecordForm(request.POST)
        if student:
            if form.is_valid():
                disciplinary_record = form.save(commit=False)
                disciplinary_record.student = student
                disciplinary_record.staff = staff
                disciplinary_record.save()
                # Handle successful form submission
                if next_page:
                    return redirect(next_page)
                return redirect('university:student-profile', student_id=student.student_id)
        else:
            # Handle invalid student ID error
            return HttpResponse("Invalid student ID", student.student_id)

    return render(request, 'university/disciplin/disciplin_form.html', {'form': form, 'current_url': current_url})


@login_required
@role_required(['is_registerar', 'is_cafe_staff', 'is_security', 'is_proctore', 'is_librarist', 'is_registral'])
def disciplinary_records(request, student_id):

    student = Student.objects.get(student_id=student_id)
    records = DisciplinaryRecord.objects.filter(
        student=student).order_by('-date')
    paginator = Paginator(records, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)

    context = {
        'records': records,
        'student_id': student.student_id,
        'current_url': request.build_absolute_uri()
    }
    return render(request, 'university/disciplin/disciplinary_records.html', context)


@login_required
@role_required(['is_registerar', 'is_cafe_staff', 'is_security', 'is_proctore', 'is_librarist', 'is_registral'])
def disciplinary_record(request, record_id):

    record = get_object_or_404(DisciplinaryRecord, id=record_id)
    return render(request, 'university/disciplin/disciplinary_record_detail.html', {'record': record})


class DisStudentListView(ListView):
    model = Student
    template_name = 'university/disciplin/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            queryset = Student.objects.filter(
                Q(student_id__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        else:
            queryset = Student.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
