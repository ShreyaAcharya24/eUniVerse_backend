import time
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.http import *
from .serializers import *
from .models import *
import base64
import json
from rest_framework import status
import os

# QR Libraries
import qrcode
from io import BytesIO


# Create your views here.

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class AlumniViewSet(viewsets.ModelViewSet):
    queryset = Alumni.objects.all()
    serializer_class = AlumniSerializer

class GuardViewSet(viewsets.ModelViewSet):
    queryset = Guard.objects.all()
    serializer_class = GuardSerializer

class DiscussionViewSet(viewsets.ModelViewSet):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer

class DocMasterViewSet(viewsets.ModelViewSet):
    queryset = DocMaster.objects.all()
    serializer_class = DocMasterSerializer

class DocRequestViewSet(viewsets.ModelViewSet):
    queryset = DocRequest.objects.all()
    serializer_class = DocRequestSerializer
















# ----------------------------------------------------------------------------------

@csrf_exempt
def hashpwd(request):
    # std = Staff.objects.get(id=3)
    # print("\n Staff 1:-",std.password)
    print(make_password("guard123"))

    return HttpResponse("Student data printed in the console")




# Admin Panel Login
@csrf_exempt
def login(request):
    return render(request,'login.html')


@csrf_exempt
def adminLogin(request): 
    if request.method == 'POST':
        uname = request.POST.get('email')
        pwd = request.POST.get('password')
        print(uname , " " , pwd)

        try:
            staff = Staff.objects.get(email=uname,password=pwd)
            print(staff)

            if (staff.is_admin=='Y' and staff is not None):
                session_id = request.session['st_id']=staff.id
                context = {'session_id' : session_id}
                return redirect('index')  # Redirect to index page on successful login
            else:
                error_message = error_message = "Not Authorised to access Admin Panel."
                return render(request, 'login.html',{'error':error_message})

        except Staff.DoesNotExist:
            error_message = error_message = "User not found with provided credentials."
            return render(request,'login.html',{'error':error_message})
    else:
        return render(request, 'login.html',{'error':'Only Post methods allowed'})

@csrf_exempt
def addDept(request):
    if request.method == 'POST':
        deptName = request.POST.get('')
        pwd = request.POST.get('')
        


@csrf_exempt
def index(request):
    session_id  = request.session.get('st_id')
    departments = Department.objects.all()
    
    if(session_id > 0):
        return render(request,'index.html',{'title':'index page','items':departments})
    else:
        print("Unauthorised to access this page")


# List Of All Students
def studentList(request):
    session_id  = request.session.get('st_id')
    students = Student.objects.select_related('div__batch__program')
    
    if(session_id > 0):
        return render(request,'students.html',{'title':'Students List Page','items':students})
    else:
        print("Unauthorised to access this page")


@csrf_exempt
def studentImage(request,s_id):
    student = Student.objects.get(id=s_id)
    image=request.FILES.get('picture')

    if not image:
            return JsonResponse({"error": "No image provided."}, status=400)
    
# Get the file extension
    extension = image.name.split('.')[-1].lower()

    if extension not in ['jpg', 'jpeg', 'png']:
        return JsonResponse({"error": "Invalid image format. Only JPG and PNG are allowed."}, status=status.HTTP_400_BAD_REQUEST)
    
    timestamp = int(time.time())
    new_filename = f"s_{s_id}_{timestamp}.{extension}"
    
    # Resize the image
    image_path = os.path.join(settings.MEDIA_ROOT, 'profile', new_filename)
    img = Image.open(image)
    img = img.resize((240, 200), Image.LANCZOS)  # Use Image.LANCZOS for high-quality downsampling

    # Save the image with appropriate options
    if extension in ['jpg', 'jpeg']:
        img.save(image_path, 'JPEG', quality=95)  # Quality parameter for JPEG
    elif extension == 'png':
        img.save(image_path, 'PNG', optimize=True)  # Optimization for PNG
    img.save(image_path)
     # Update student picture path
    student.picture = f"profile/{new_filename}"
    student.save()
    return JsonResponse({"message": "Image uploaded successfully!"}, status=status.HTTP_200_OK)
    


def studentDetails(request,s_id):
    session_id  = request.session.get('st_id')
    
    if session_id == 0:
        raise Http404("Unauthorized to access this page")
    else:
        try:
            # Get the student with the specified ID, including related objects
            student = Student.objects.select_related('div__batch__program').get(id=s_id)
            return render(request,'studentDetail.html',{'title':'Students List Page','items':student})
        except Student.DoesNotExist:
            raise Http404("Student does not exist")


def studentUpdate(request,s_id):
    session_id  = request.session.get('st_id')

    if session_id == 0:
        raise Http404("Unauthorized to access this page")
    else:
        try:
            # Get the student with the specified ID, including related objects
            student = Student.objects.select_related('div__batch__program').get(id=s_id)
            divisions = Division.objects.all()
            batches = Batch.objects.all()
            programs = Program.objects.all()
            departments = Department.objects.all()
            
            return render(request,'studentUpdate.html',
                          {'title':'Student Update',
                            'items':student,
                            'divisions': divisions,
                            'batches': batches,
                            'programs': programs,
                            'departments': departments})
        except Student.DoesNotExist:
            raise Http404("Student does not exist")

@csrf_exempt
def updateStudentDetails(request,s_id):

    if request.method == 'POST':
        # Retrieve form data
        enrolment_no = request.POST.get('enrolment_no')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        isactive = request.POST.get('isactive')
        street_name = request.POST.get('street')
        city = request.POST.get('city')
        pin = request.POST.get('pin')
        state = request.POST.get('state')
        division_id = request.POST.get('division')
        divi = Division.objects.get(div_id=division_id)
        student = Student.objects.get(id=s_id)

        print("data: ", first_name)
    
        # Update student object with new values
        student.enrolment_no = enrolment_no
        student.first_name = first_name
        student.middle_name = middle_name
        student.last_name = last_name
        student.contact = contact
        student.email=email
        student.isactive = isactive
        student.street_name = street_name
        student.city = city
        student.pin = pin
        student.state = state
        student.div = divi
        
        # Save the updated student object
        student.save()
        
        return redirect("index")  # Redirect to student list page after update
        
    else:
        return render(request, 'update_student_details.html', {'student': student})

def studentDelete(request,s_id):
    # session_id  = request.session.get('st_id')
    # if session_id == 0:
    #     raise Http404("Unauthorized to access this page")
    # else:
    try:
        student = Student.objects.get(id=s_id)
        student.delete()
        return redirect("index")
    except:
        return HttpResponse("Deletion Failed")

 
    
def doc_request(request):
    session_id  = request.session.get('st_id')
    docreqs= DocRequest.objects.filter(isapproved='P')
    
    if(session_id > 0):
        return render(request,'ViewDocRequests.html',{'title':'Document Requests','items':docreqs})
    else:
        print("Unauthorised to access this page")

def discussions(request):
    session_id  = request.session.get('st_id')
    students = Student.objects.all()
    
    if(session_id > 0):
        return render(request,'students.html',{'title':'index page','students':students})
    else:
        print("Unauthorised to access this page")

def approveReqEmail(request, requester_role, requester_id,doc_id):
    try:
        if requester_role == 'Student':
            requester = Student.objects.get(enrolment_no=requester_id)
            requester_email = requester.email
        elif requester_role == 'Alumni':
           requester = Alumni.objects.get(enrolment_no=requester_id)
           requester_email = requester.email

        print("email:",requester_email)

        subject = "Document Request Approved"
        to_email = requester_email
        message = f"Your Request for the document has been approved. You will be sent an email once it is prepared to collect from admin office."
        recipient_list = [to_email]
        send_mail(subject, message, to_email,recipient_list)

        DocRequest.objects.filter(doc_id=doc_id).update(isapproved='Y')

        return HttpResponse("Email Successfully Sent toemail: {}".format(requester_email))
    

    except Exception as e:
        print(e)
        return HttpResponse("Email Sending Failed. Kindly Verify if it is valid:{}".format(requester_email))

@csrf_exempt
def createDepartment(request):
    return render(request,'create_department.html',{'title':'Create Department'})



# *******************************************************************************
#  Mobile APIs
# *******************************************************************************
def getDocCategories(request):
    if request.method == 'GET':
        try:
            data = json.loads(request.body)
            role = data.get('role')

            if(role == 'Student'):
                categories = DocMaster.objects.filter(isoffered='Y',offeredto__in =['S','B']).values('docm_id', 'doc_name')
                return JsonResponse({'categories': list(categories)})
            else:
                categories = DocMaster.objects.filter(isoffered='Y',offeredto__in=['A','B']).values('docm_id', 'doc_name')
                return JsonResponse({'categories': list(categories)})

        except:
            return JsonResponse({"msg": "Failed to load the categories"},status=404)
    else: 
        return JsonResponse({"error":"Only GET Method is Allowed"},status=405)

@csrf_exempt
def createDocReq(request):
    if request.method == 'POST':
        try:
            # Hidden in form
            f_role = request.POST.get('requester_role')
            f_enrolment = request.POST.get('requester_enrolment')
            
            # Show in form
            f_name = request.POST.get('full_name')
            f_doc_id = request.POST.get('doc_id')
            f_doc_name = request.POST.get('doc_name')
            f_num_of_copies = request.POST.get('num_of_copies')
            f_purpose = request.POST.get('purpose')
            f_additional_instructions = request.POST.get('additional_instructions')

            uploaded_file = request.FILES.get('uploaded_pdf')
            masterdoc = DocMaster.objects.get(docm_id=f_doc_id)

            if uploaded_file:

                timestamp = timezone.now().strftime("%d%m%Y")
                file_name = f"{f_enrolment}_{timestamp}.pdf"

                upload_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
                file_path = os.path.join(upload_dir, file_name)
                
                with open(file_path, 'wb+') as destination:
                # Iterate over the chunks of the uploaded file
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                
                docreq = DocRequest.objects.create(
                    docm=masterdoc,
                    requester_id=f_enrolment,
                    requester_role=f_role,
                    full_name=f_name,
                    purpose=f_purpose,
                    no_of_copies=f_num_of_copies,
                    additional_instructions=f_additional_instructions,
                    doc_file=file_path
                    )
                
                return JsonResponse({'message': 'PDF file uploaded successfully'},status=201)
            else:
                 return JsonResponse({'error': 'Please upload pdf of necessary documents'},status=403)
        except IOError:
            return JsonResponse({'error': 'An error occurred while reading or writing the file'},status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)},status=404)
    
    else:
        return JsonResponse({"error": "Only POST Method is Allowed"},status=405)
    
class InvalidCredentialsError(Exception):
    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(self.message)


verKey = "$2a$16$qljF5CC2.VLt5sUgKggTMOZ6xpGGwSxGweKtqE.FtAR9jiNd4xLDS"

@csrf_exempt
def getUser(request):
    # Check if the request method is POST
    if request.method == "POST":

        # Load JSON data from request body
        data = json.loads(request.body)

        # Extract username and password from flutter JSON data
        f_uname = data.get("username", None)
        f_pwd = data.get("password", None)
        f_role = data.get("role", None)


        # Check if the user exists in database ?
        # table fields
        try:
            json_string = ""
            response_data = {"user_data": "", "user_qr": ""}
            match f_role:

                # if User is Student
                case "Student":
                    try:
                        student = Student.objects.get(
                            enrolment_no=f_uname, password=f_pwd
                        )
                        # Student's division is a fk therefor it returns and instance of Division model
                        # since we got division object now from that we can get div-id and batch of that particular div which is again an instance of batch
                        s_div = student.div
                        s_batch = s_div.batch
                        s_program = s_batch.program
                        s_dept = s_program.dep

                        # Construct the path to the image file based on the enrollment number
                        image_filename = f"{student.enrolment_no}.jpg"
                        image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_filename)

                        if os.path.exists(image_path):
                            # Open the image file and read its content
                                with open(image_path, 'rb') as image_file:
                                # Encode the image content to base64
                                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        else:
                            # If the requested image file does not exist, load the default image
                            default_image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'default.png')
                            with open(default_image_path, 'rb') as default_image_file:
                                image_data = base64.b64encode(default_image_file.read()).decode('utf-8')

                        student_data = {
                            "enrolment": student.enrolment_no,
                            "name": student.first_name + " " + student.last_name,
                            "email": student.email,
                            "pwd": student.password,
                            "contact": student.contact,
                            "street_name": student.street_name,
                            "city": student.city,
                            "state": student.state,
                            "pin": student.pin,
                            "role": f_role,
                            "div": s_div.div_name,
                            "batch_start_year": s_batch.start_year,
                            "batch_duration": s_batch.duration,
                            "program_name": s_program.program_name,
                            "program_abbr": s_program.program_abbr,
                            "dept_name": s_dept.dep_name,
                            "dept_abbr": s_dept.dep_abbr,
                            "profile": image_data
                        }

                        response_data["user_data"] = student_data

                        qr_data = {
                            "enrolment": student.enrolment_no,
                            "role": f_role,
                            "program_abbr": s_program.program_abbr,
                            "key": verKey,
                        }

                        # Convert json into string
                        json_string = json.dumps(qr_data)

                    except Student.DoesNotExist:
                        return JsonResponse(
                            {"error": "Invalid Role Selected"}, status=406
                        )

                # if User is Alumni
                case "Alumni":
                    try:
                        alumni = Alumni.objects.get(
                            enrolment_no=f_uname, password=f_pwd
                        )
                        a_div = alumni.div
                        a_batch = a_div.batch
                        a_program = a_batch.program
                        a_dept = a_program.dep

                        # Construct the path to the image file based on the enrollment number
                        image_filename = f"{alumni.enrolment_no}.png"
                        image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_filename)

                        if os.path.exists(image_path):
                            # Open the image file and read its content
                                with open(image_path, 'rb') as image_file:
                                # Encode the image content to base64
                                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        else:
                            # If the requested image file does not exist, load the default image
                            default_image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'default.png')
                            with open(default_image_path, 'rb') as default_image_file:
                                image_data = base64.b64encode(default_image_file.read()).decode('utf-8')


                        alumni_data = {
                            "enrolment": alumni.enrolment_no,
                            "name": alumni.first_name + " " + alumni.last_name,
                            "email": alumni.email,
                            "pwd": alumni.password,
                            "contact": alumni.contact,
                            "street_name": alumni.street_name,
                            "city": alumni.city,
                            "state": alumni.state,
                            "pin": alumni.pin,
                            "role": f_role,
                            "div": a_div.div_name,
                            "batch_start_year": a_batch.start_year,
                            "batch_duration": a_batch.duration,
                            "program_name": a_program.program_name,
                            "program_abbr": a_program.program_abbr,
                            "dept_name": a_dept.dep_name,
                            "dept_abbr": a_dept.dep_abbr,
                            "profile": image_data
                        }

                        response_data["user_data"] = alumni_data

                        qr_data = {
                            "enrolment": alumni.enrolment_no,
                            "role": f_role,
                            "program_abbr": a_program.program_abbr,
                            "key": verKey,
                        }

                        # Convert json into string
                        json_string = json.dumps(qr_data)

                    except Alumni.DoesNotExist:
                        return JsonResponse(
                            {"error": "Invalid Role Selected"}, status=406
                        )

                case "Staff":
                    try:
                        staff = Staff.objects.get(email=f_uname, password=f_pwd)
                        st_dep = staff.dep

                        # Construct the path to the image file based on the enrollment number
                        image_filename = f"{staff.email}.png"
                        image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_filename)

                        if os.path.exists(image_path):
                            # Open the image file and read its content
                                with open(image_path, 'rb') as image_file:
                                # Encode the image content to base64
                                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        else:
                            # If the requested image file does not exist, load the default image
                            default_image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'default.png')
                            with open(default_image_path, 'rb') as default_image_file:
                                image_data = base64.b64encode(default_image_file.read()).decode('utf-8')


                        staff_data = {
                            "name": staff.first_name + " " + staff.last_name,
                            "email": staff.email,
                            "pwd": staff.password,
                            "contact": staff.contact,
                            "street_name": staff.street_name,
                            "city": staff.city,
                            "pin": staff.pin,
                            "role": f_role,
                            "dept_name": st_dep.dep_name,
                            "dept_abbr": st_dep.dep_abbr,
                            "profile": image_data
                        }

                        response_data["user_data"] = staff_data

                        qr_data = {
                            "email": staff.email,
                            "role": f_role,
                            "dept_abbr": st_dep.dep_abbr,
                            "key": verKey,
                        }

                        # Convert json into string
                        json_string = json.dumps(qr_data)

                    except Staff.DoesNotExist as e:
                        return JsonResponse(
                            {"error": "Invalid Role Selected"}, status=400
                        )

                case "Guard":
                    try:
                        guard = Guard.objects.get(email=f_uname, password=f_pwd)
                        g_dep = guard.dep

                        # Construct the path to the image file based on the enrollment number
                        image_filename = f"{guard.email}.png"
                        image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_filename)

                        if os.path.exists(image_path):
                            # Open the image file and read its content
                                with open(image_path, 'rb') as image_file:
                                # Encode the image content to base64
                                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        else:
                            # If the requested image file does not exist, load the default image
                            default_image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'default.png')
                            with open(default_image_path, 'rb') as default_image_file:
                                image_data = base64.b64encode(default_image_file.read()).decode('utf-8')


                        guard_data = {
                            "name": guard.first_name + " " + guard.last_name,
                            "email": guard.email,
                            "pwd": guard.password,
                            "contact": guard.contact,
                            "street_name": guard.street_name,
                            "city": guard.city,
                            "pin": guard.pin,
                            "role": f_role,
                            "dept_name": g_dep.dep_name,
                            "dept_abbr": g_dep.dep_abbr,
                            "profile": image_data
                        }

                        response_data["user_data"] = guard_data

                        qr_data = {
                            "email": guard.email,
                            "role": f_role,
                            "dept_abbr": g_dep.dep_abbr,
                            "key": verKey,
                        }

                        # Convert json into string
                        json_string = json.dumps(qr_data)

                    except Guard.DoesNotExist as e:
                        return JsonResponse(
                            {"error": "Invalid Role Selected"}, status=406
                        )

            # Generate QR code Image
            qr_image = qrcode.make(json_string)
            qr_image_pil = qr_image.get_image()
            stream = BytesIO()
            qr_image_pil.save(stream, format="PNG")
            qr_image_data = stream.getvalue()
            qr_image_base64 = base64.b64encode(qr_image_data).decode("utf-8")

            response_data["user_qr"] = qr_image_base64

            return JsonResponse({"data": response_data}, status=200)

        except InvalidCredentialsError as e:
            return JsonResponse({"error": e.message}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)




