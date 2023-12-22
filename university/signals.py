from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import date

from .models import Student, Meal, CafeAttendance


@receiver(post_save, sender=Student)
def create_meal_service(sender, instance, created, **kwargs):
    if created and instance.is_cafe_user:
        meals = Meal.objects.filter(
            start_date__lte=date.today(), end_date__gte=date.today())
        for meal in meals:
            CafeAttendance.objects.create(student=instance, meal=meal)


@receiver(post_save, sender=Meal)
def create_meal_service(sender, instance, created, **kwargs):
    if created and instance.meal_period in ['breakfast', 'lunch', 'dinner']:
        current_cafe_users = Student.objects.filter(
            is_cafe_user=True, is_active=True)

        for student in current_cafe_users:
            CafeAttendance.objects.create(student=student, meal=instance)


@receiver(pre_save, sender=Student)
def update_meal_service(sender, instance, **kwargs):
    try:
        original_student = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field hasn't technically changed yet
        pass
    else:
        # Check if is_active or is_cafe_user field has changed
        if (not original_student.is_active and instance.is_active and instance.is_cafe_user) or (original_student.is_cafe_user != instance.is_cafe_user):
            # Student has changed from inactive to active and is a cafe user, or is_cafe_user field has changed
            if instance.is_cafe_user and instance.is_active:
                meals = Meal.objects.filter(
                    meal_period__in=['breakfast', 'lunch', 'dinner'])
                for meal in meals:
                    if not CafeAttendance.objects.filter(student=instance, meal=meal).exists():
                        CafeAttendance.objects.create(
                            student=instance, meal=meal)
            else:
                CafeAttendance.objects.filter(student=instance, meal__meal_period__in=[
                    'breakfast', 'lunch', 'dinner']).delete()

        if (original_student.is_active and not instance.is_active):
            CafeAttendance.objects.filter(student=instance, ).delete()
