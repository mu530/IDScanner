from django.urls import path
from . import views

app_name = 'university'
urlpatterns = [
     path('', views.index, name='home'),
     path('about/', views.about_us, name='about_us'),
     path('staff/password/', views.ChangePasswordView.as_view(), name='password_change'),
     path('staff/<int:pk>', views.staff_update, name='staff_update'),
     path('staffs/registor/', views.create_staff, name='register-staff'),
     path('view_card/', views.view_scan, name='view-card'),
     path('view_card/<str:student_id>/', views.view_card, name='view-id'),
     path('login/', views.loginPage, name='login'),
     path("logout/", views.LogoutView.as_view(), name="logout"),


     # Student registration and QR code generation module
     path('student/registor/', views.student_form, name='register-student'),
     path('students/', views.students_list, name='list-students'),
     path('student_profile/<str:student_id>',
          views.student_profile, name='student-profile'),
     path('student_profile/update/<str:student_id>',
          views.update_student_profile, name='student-profile-update'),
     path('student_profile/add_device/<str:student_id>',
          views.add_device, name='add-device'),
     path('staffs/add/uni_info/', views.university_form,
          name='add-university-info'),
     path('staffs/list/uni_info/', views.department_list,
          name='department-list'),


     # Cafeteria service module
     path('cafe/', views.cafe_maneger, name='cafe-manager'),
     path('cafe/form/', views.cafe_form, name='cafe-form'),
     path('cafe/eat/<str:pk>', views.eat_meal, name='eat-meal'),
     path('cafe/coupon/add/', views.add_coupon, name='add-coupon'),
     path('cafe/coupon/list/', views.CouponListView.as_view(), name='list-coupon'),
     path('cafe/coupon/<int:coupon_id>/',
          views.coupon_detail, name='coupon-detail'),
     path('cafe/coupon/delete/<int:coupon_id>/',
          views.CouponDeleteView.as_view(), name='delete-coupon'),
     path('cafe/add_coupon_to_students/', views.add_coupon_to_students,
          name='add-coupon-to-students'),
     path('cafe/student/detail/<str:student_id>/', views.cafe_user_detail,
          name='cafe-student-detail'),


     # Library module
     path('library/', views.LibraryListView.as_view(), name='library-manager'),
     path('library/<int:pk>/return/', views.book_return, name='library-return'),
     path('library/add_book/', views.add_book, name='add-book'),
     path('library/students/', views.library_student_list,
          name='student-book-rent'),
     path('library/book-rental/<str:student_id>/',
          views.book_rental_page, name='book-rental-page'),
     path('library/book-rental/<str:student_id>/<int:book_id>/rent/',
          views.rent_book, name='rent-book'),

     # Disciplinary recording module
     path('disciplin/',
          views.DisStudentListView.as_view(), name='disciplin-student-list'),
     path('disciplin/record/<str:student_id>/',
          views.add_disciplinary_record, name='disciplin-form'),
     path('disciplin/list/<str:student_id>/',
          views.disciplinary_records, name='disciplin-list'),
     path('disciplin/recored/<int:record_id>/',
          views.disciplinary_record, name='disciplin-recored-detail'),


]
