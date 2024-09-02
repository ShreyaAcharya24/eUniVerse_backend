"""
URL configuration for capstoneAPIs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from ast import Index
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path,include
from adminAPIs.views import *
from adminAPIs.userviews import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'departments',DepartmentViewSet)
router.register(r'staff',StaffViewSet)
router.register(r'programs',ProgramViewSet)
router.register(r'divisions',DivisionViewSet)
router.register(r'batches',BatchViewSet)
router.register(r'students',StudentViewSet)
router.register(r'alumni',AlumniViewSet)
router.register(r'discussions',DiscussionViewSet)
router.register(r'guards',GuardViewSet)
router.register(r'docs',DocMasterViewSet)
router.register(r'docreqs',DocRequestViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(router.urls)),

    # Mobile APIs
    path('user-login/', user_login, name='user_login'),
    path('user-profile/', user_profile, name='user_profile'),
    path('token-verify/', token_verify, name='token_verify'),
    path('generate-qr/', generate_qr_code, name='generate_qr'),
    path("scan-qr/",scan_qr_code,name="scan_qr"),

    path('create-post/',createPost,name="create_post"),
    path('view-posts/',getApprovedPosts,name="view_posts"),


    path('hash/', hashpwd, name='hash'),
    path('api/token/',at,name="at"),

# ******************************************************************************************
    # html file
    path('index/',index,name='index'),
    path('studentList/',studentList,name='studentList'),
    # path('index/',index,name='index'),
    path('adlogin/',login,name='login'),
    path('doc_requests/',doc_request,name='doc_requests'),
    path('discussions/',discussions,name='discussions'),

    path('approveReqEmail/<str:requester_role>/<str:requester_id>/<int:doc_id>',approveReqEmail, name='approveReqEmail'),
    path('studentDetails/<int:s_id>',studentDetails,name="studentDetails"),
    path('studentUpdate/<int:s_id>',studentUpdate,name="studentUpdate"),
    path('updateStudentDetails/<int:s_id>',updateStudentDetails,name='updateStudentDetails'),
    path('studentDelete/<int:s_id>',studentDelete,name="studentDelete"),
    path('student-image/<int:s_id>',studentImage,name='student_image'),
    
    
    
    # admin
    path('adminlogin/',adminLogin,name='adminlogin'),
    path('create_department/',createDepartment,name='create_department'),
     path('add_Dept/',addDept,name='addDept'),

    # user
     path('get_user/',getUser,name="get-user"),
    path('create_docreq/',createDocReq,name="create-docreq"),
    path('get_doccategories/',getDocCategories,name="get-doccategories")

    # path('department_list/',departmentList,name='department_list')    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)