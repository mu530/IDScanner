from django.urls import path

from . import views

urlpatterns = [
    path('auth/', views.login),
    path('students/', views.getAllStudent),
    path('student/<str:id>', views.getStudent, name='student'),
    #     path('address/', views.getAddress, name='address'),
    #     path('devices/', views.getDevice, name='devices'),
    path('meal/', views.getMeal, name='meal'),
    #     path('cafe_attendance/', views.getCafeAttendance, name='cafe_attendance'),
    path('cafe_attendance/',
         views.getCafeAttendance, name='cafe_attendance_update'),
    path('add_disciplinary_record/', views.createDisciplinaryRecord,
         name='add_disciplinary_record'),

]
