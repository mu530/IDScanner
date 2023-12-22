from rest_framework import serializers
from django.contrib.auth.models import User
from university.models import *


# class UserRoleSerializer(serializers.ModelSerializer):
#     class Meta(object):
#         model = UserRole
#         fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = '__all__'


class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = '__all__'


class FieldSerializer(serializers.ModelSerializer):
    campus = CampusSerializer(read_only=True)

    class Meta:
        model = Field
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)

    class Meta:
        model = Department
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    emergency = EmergencyContactSerializer(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'


class CafeAttendanceSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = CafeAttendance
        fields = '__all__'


class CafeAttendanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeAttendance
        fields = ['has_eaten']


class DisciplinaryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplinaryRecord
        fields = ['student', 'staff', 'reason']
