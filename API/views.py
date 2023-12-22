from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from university.models import *
from .serializers import *


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)


    return Response({'token': token.key, 'user': serializer.data})


@api_view(['GET'])
def getStudent(request, id):
    try:
        student = Student.objects.get(student_id=id)
        devices = Device.objects.filter(student=student)
        device_serializer = DeviceSerializer(
            devices, many=True).data if devices.exists() else None
        student_serializer = StudentSerializer(student, many=False).data

        return Response({'student': student_serializer, 'devices': device_serializer}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response('Student not found', status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def getAllStudent(request):

    if request.method == 'GET':
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def getMeal(request):
    if request.method == 'GET':
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MealSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def getCafeAttendance(request):
    student_id = request.data.get('student_id')
    meal_id = request.data.get('meal_id')

    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=400)
    try:
        meal = Meal.objects.get(id=meal_id)
    except Meal.DoesNotExist:
        return Response({'error': 'Meal Period not found'}, status=400)

    if not student.is_cafe_user:
        return Response({'error': f'{student.first_name} {student.last_name} is not a cafe user.'}, status=403)

    try:
        attendance = CafeAttendance.objects.get(student=student, meal=meal)
    except CafeAttendance.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CafeAttendanceSerializer(attendance, many=False)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if attendance.has_eaten:
            return Response({'error': f'{student.first_name} {student.last_name} has already attended this meal program.'}, status=400)
        attendance.has_eaten = True
        attendance.save()
        serializer = CafeAttendanceSerializer(attendance, many=False)
        return Response({'message': f'{student.first_name} {student.last_name} has successfully attended this meal program.'}, status=200)

    elif request.method == 'DELETE':
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createDisciplinaryRecord(request):
    student_id = request.data.get('student_id')
    reason = request.data.get('reason')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=400)

    staff = request.user  # Get the currently authenticated staff user from the token

    disciplinary_record = DisciplinaryRecord(
        student=student, staff=staff, reason=reason)
    disciplinary_record.save()

    serializer = DisciplinaryRecordSerializer(disciplinary_record)
    return Response(serializer.data, status=201)
