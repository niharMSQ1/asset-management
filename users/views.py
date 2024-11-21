from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import authenticate


# Create your views here.
def test(request):
    return JsonResponse({

    })

@csrf_exempt
@api_view(['POST'])
def create_user(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied. Contact Admin.'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not supported. Only POST requests are allowed.'}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')


        if not username or not email or not password:
            return JsonResponse({'error': 'All fields (username, email, password) are required.'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists.'}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password) 
        )



        return JsonResponse({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            user = authenticate(username=username, password=password)

            if user is not None:
                deleteToken = (OutstandingToken.objects.filter(user=user)).delete()
                refresh = RefreshToken.for_user(user)

                return JsonResponse({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                }, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
def test(request):
    return JsonResponse({
        "message":"Hello World!"
    })