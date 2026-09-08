from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new student or instructor [LMS-AUTH-01]."""
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', User.Role.STUDENT)

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password, role=role)
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': {
            'id': str(user.id),
            'username': user.username,
            'role': user.role,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)
