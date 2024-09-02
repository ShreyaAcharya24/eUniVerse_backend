from django.contrib.auth.backends import BaseBackend
from .models import Student, Alumni, Staff, Guard
from django.contrib.auth.hashers import check_password

class CustomUserBackend(BaseBackend):
    def authenticate(self,request,username,password,role):
        if role == 'Student':
            try:
                user=Student.objects.get(enrolment_no=username)
            except Student.DoesNotExist:
                return None
            
        elif role == 'Alumni':
            try:
                user=Alumni.objects.get(enrolment_no=username)
            except Alumni.DoesNotExist:
                return None
            
        elif role == 'Staff':
            try:
                user = Staff.objects.get(email=username)
                print("Staff email:--- ",user.email)
            except Staff.DoesNotExist:
                return None
            
        elif role == 'Guard':
            try:
                user = Guard.objects.get(email=username)
            except Guard.DoesNotExist:
                return None
        
        # print(user.password)
        if user and check_password(password, user.password):
            return user
        
        return None
        
    def get_user(self, user_id):
        user = None
        if Student.objects.filter(student_id=user_id).exists():
            user = Student.objects.get(student_id=user_id)
        elif Alumni.objects.filter(alumni_id=user_id).exists():
            user = Alumni.objects.get(alumni_id=user_id)
        elif Staff.objects.filter(staff_id=user_id).exists():
            user = Staff.objects.get(staff_id=user_id)
        elif Guard.objects.filter(guard_id=user_id).exists():
            user = Guard.objects.get(guard_id=user_id)
        return user
    