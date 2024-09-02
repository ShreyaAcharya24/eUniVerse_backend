import json
import os
from adminAPIs.serializers import TokenSerializer
from .models import *
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import *
from rest_framework_simplejwt.exceptions import InvalidToken,TokenError
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist

# ***********************************************************
import qrcode
import base64
from io import BytesIO
from django.utils.timezone import now
from cryptography.fernet import Fernet
 


# Generate a key for encryption (Do this once and store the key securely)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt the data
@csrf_exempt
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

# Decrypt the data
@csrf_exempt
def decrypt_data(token):
    return cipher_suite.decrypt(token).decode()

@csrf_exempt
def generate_qr_code(request):
    if request.method == 'POST':
        
        # Verify Bearer token
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or not a Bearer token'}, status=400)

        # Decode the token to get the user ID
        token_str = auth_header.split(' ')[1]
        try:
            token = AccessToken(token_str)
            user_id = token['user_id']
            
            data = json.loads(request.body)
            user_role = data.get('role',None)

            print("##User Id",user_id)
            print("##USer_role",user_role)
        
        except (InvalidToken, TokenError):
            return JsonResponse({'error': 'Invalid token'}, status=401)

    # Prepare data for the QR code
    qr_data = f"{user_id}:{user_role}"
    
    # Encrypt the data
    encrypted_data = encrypt_data(qr_data)
    print("^^^ -- ",encrypted_data)
    
    # Generate the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(encrypted_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')

    # Convert the image to base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    return JsonResponse({
        'qr_code': qr_base64,
        'role': user_role,
        'generated_on': now(),
    },status=200)


# Decrypt QR
@csrf_exempt
@api_view(['POST'])
def scan_qr_code(request):
    try:
        # Parse the incoming JSON request body
        data = json.loads(request.body)
        qr_code_data = data.get('qr_code')

        if not qr_code_data:
            return JsonResponse({'error': 'QR code data is missing'}, status=400)

        # Attempt to decrypt the QR code data
        try:
            qr_code_data_bytes = qr_code_data.encode('utf-8')
            decrypted_data = decrypt_data(qr_code_data_bytes)
        except Exception as e:
            return JsonResponse({'error': 'Failed to decrypt QR code data', 'details': str(e)}, status=400)

        print("Decrypted Data:", decrypted_data)

        try:
            # Expecting the decrypted data to be in the format 'user_id:user_role'
            user_id, user_role = decrypted_data.split(':')
        except ValueError:
            return JsonResponse({'error': 'Invalid QR code data format'}, status=400)

        print("\n@@@@ ", user_id, "  --  ", user_role)

        # Fetch user details based on the role
        try:
            if user_role == 'Student':
                user = Student.objects.get(id=user_id)
            elif user_role == 'Alumni':
                user = Alumni.objects.get(id=user_id)
            elif user_role == 'Staff':
                user = Staff.objects.get(id=user_id)
            else:
                return JsonResponse({'error': 'Invalid role in QR code'}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({'error': f'No user found for ID: {user_id} and role: {user_role}'}, status=404)

        print("User Object:", user)

        # Handle the user's profile picture
        if user.picture:
            picture_path = user.picture.path
        else:
            picture_path = os.path.join(settings.MEDIA_ROOT, 'profile', 'default.png')

        try:
            with open(picture_path, "rb") as image_file:
                picture_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            return JsonResponse({'error': 'Profile picture not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error reading profile picture', 'details': str(e)}, status=500)

        # Prepare response data
        response_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_picture': picture_base64
        }

        if user_role in ['Student', 'Alumni']:
            response_data.update({
                'batch_s': user.div.batch.start_year,
                'batch_e': user.div.batch.start_year + user.div.batch.duration,
                'program_name': user.div.batch.program.program_name,
                'program_abbr': user.div.batch.program.program_abbr,
                'enrolment_no': user.enrolment_no,
            })
        else:
            response_data.update({
                'joining': user.joining_date,
                'department_name': user.dep.dep_name,
            })

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

# ***********************************************************************************************

@api_view(['POST'])
def token_verify(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        try:
            # Validate the token using SimpleJWT
            AccessToken(token)  # This will raise an exception if the token is invalid
            return JsonResponse({'valid': True}, status=200)
        except (TokenError, InvalidToken) as e:
            # If token is invalid, return an error response
            return JsonResponse({'valid': False, 'error': str(e)}, status=401)
    else:
        return JsonResponse({'error': 'Invalid data'}, status=400)


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
  
        if not username or not password or not role:
            return JsonResponse({'error': 'Please provide username, password, and role'}, status=400)

        user = authenticate(request, username=username, password=password, role=role)
        if user:
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': role,
                'id':user.id
            }, status=200)
        return JsonResponse({'error': 'Invalid Credentials'}, status=401)


@csrf_exempt
def user_profile(request):
    if request.method == 'GET':
        # Verify Bearer token
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or not a Bearer token'}, status=400)

        # Decode the token to get the user ID
        token_str = auth_header.split(' ')[1]
        try:
            token = AccessToken(token_str)
            user_id = token['user_id']
            print("USer Id",user_id)
        except (InvalidToken, TokenError):
            return JsonResponse({'error': 'Invalid token'}, status=401)

        # Determine the user role and fetch the profile
        user_role = request.GET.get('role', None)
        print("User rolee:-- ", user_role)

        program = ''
        user = None
        if user_role == 'Student' and Student.objects.filter(id=user_id).exists():
            user = Student.objects.get(id=user_id)
            program = user.div.batch.program.program_abbr
            enrolment = user.enrolment_no
        elif user_role == 'Alumni' and Alumni.objects.filter(id=user_id).exists():
            user = Alumni.objects.get(id=user_id)
            program = user.div.batch.program.program_abbr
            enrolment = user.enrolment_no
        elif user_role == 'Staff' and Staff.objects.filter(id=user_id).exists():
            user = Staff.objects.get(id=user_id)
            program = user.dep.dep_abbr
        elif user_role == 'Guard' and Guard.objects.filter(id=user_id).exists():
            user = Guard.objects.get(id=user_id)
            program = user.dep.dep_abbr
        else:
            return JsonResponse({'error': 'User not found or invalid role'}, status=404)

        # Convert profile picture to base64
        if user.picture:
            picture_path = user.picture.path
        else:
             picture_path = os.path.join(settings.MEDIA_ROOT, 'profile', 'default.png')

        with open(picture_path, "rb") as image_file:
            picture_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        response_data = {
            'name': f'{user.first_name} {user.last_name}',
            'profile_picture': picture_base64,
            'program': program,
            'email': user.email
        }

        # Include 'enrolment' for Student and Alumni roles
        if user_role in ['Student', 'Alumni']:
            response_data['enrolment'] = enrolment
        return JsonResponse(response_data, status=200)


@csrf_exempt
def createPost(request):
    if request.method=='POST':

        # Load JSON data from request body
        data = json.loads(request.body)

        # Extract Post Data from flutter JSON data
        posted_by = data.get("id", None)
        post_title = data.get("post_title", None)
        post_content = data.get("post_content", None)

        try:
            alumni = Alumni.objects.get(id=posted_by)
        except Alumni.DoesNotExist:
            return JsonResponse({"error": "Alumni not found"}, status=404)

        # Create the discussion

        discussion = Discussion.objects.create(posted_by=alumni, post_title=post_title, post_content=post_content)
        # discussion.postdate
        return JsonResponse({"success": "Post created successfully"}, status=201)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


# get all the approved posts
def getApprovedPosts(request):
    if request.method=='GET':
        # Retrieve approved posts with related alumni and their program
        approved_posts = Discussion.objects.filter(isapproved='Y').select_related(
            'posted_by', 'posted_by__div__batch__program'
        ).order_by('-post_date')

        # Create a list to store post data
        post_data = []

        # Iterate over approved posts and construct the data dictionary for each post
        for post in approved_posts:
            post_data.append({
                'post_title': post.post_title,
                'post_content': post.post_content,
                'post_date': post.post_date,
                'posted_by_first_name': post.posted_by.first_name,
                'posted_by_last_name': post.posted_by.last_name,
                'program_abbr': post.posted_by.div.batch.program.program_abbr
            })

        # Convert the list of dictionaries to JSON format
        json_data = {"posts":post_data}

        # Return JSON response
        return JsonResponse(json_data,status=201)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


def at(request):
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE3MTAwODYzLCJpYXQiOjE3MTY2Njg4NjMsImp0aSI6ImMyYzM3MTYwMzIyOTQ5YWRhMGZlZjNjZTMwODlhOGUxIiwidXNlcl9pZCI6MX0.5PYkVND6JF7jp_9KpClbddrNuRa0wLnHbnWD34kcIXU"

    decoded_token = AccessToken(token=access_token)
    print(decoded_token.payload)