from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from api.serializers import UserSerializer, ApartmentSerializer
from api.permissions import IsAdminRole, IsOwnerOrReadOnly
from api.models import Apartment, UserConfig

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class LoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return Response(data = {
                "token": jwt_encode_handler(jwt_payload_handler(user)),
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "email": user.email,
                    "role": user.config.role
                },
            })

        return Response(data={
            "detail": "Invalid username or password"
        }, status=status.HTTP_400_BAD_REQUEST)

class SignupView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = User.objects.all().filter(~Q(config__role=UserConfig.USER_ROLE_ADMIN))

        role = self.request.query_params.get('role', None)
        if role is not None:
            qs = qs.filter(config__role=role)

        return qs

class ApartmentViewSet(viewsets.ModelViewSet):
    model = Apartment
    serializer_class = ApartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Apartment.objects.all()
        if self.request.user.config.role == UserConfig.USER_ROLE_CLIENT:
            qs = qs.filter(status=Apartment.APARTMENT_AVAILABLE)
        elif self.request.user.config.role == UserConfig.USER_ROLE_REALTOR:
            qs = qs.filter(realtor=self.request.user)

        size = self.request.GET.getlist('size[]')
        if len(size) > 0:
            qs = qs.filter(size__gte=size[0], size__lte=size[1])

        price = self.request.GET.getlist('price[]')
        if len(price) > 0:
            qs = qs.filter(price__gte=price[0], price__lte=price[1])

        rooms = self.request.GET.getlist('rooms[]')
        if len(rooms) > 0:
            qs = qs.filter(rooms__gte=rooms[0], rooms__lte=rooms[1])

        return qs.order_by('-added_date').order_by('price')

    def perform_create(self, serializer):
        realtor_id = self.request.data.get('realtor_id', None)
        if realtor_id is not None:
            realtor = User.objects.get(id=realtor_id)
        else:
            realtor = self.request.user

        if realtor.config.role != UserConfig.USER_ROLE_REALTOR:
            return Response(data={
                "detail": "A user should be realtor"
            }, status=status.HTTP_400_BAD_REQUEST)

        apartment = serializer.save(realtor=realtor)
        apartment.save()

    def perform_update(self, serializer):
        realtor_id = self.request.data.get('realtor_id', None)
        if realtor_id is not None:
            realtor = User.objects.get(id=realtor_id)
        else:
            realtor = self.request.user

        if realtor.config.role != UserConfig.USER_ROLE_REALTOR:
            return Response(data={
                "detail": "A user should be realtor"
            }, status=status.HTTP_400_BAD_REQUEST)

        apartment = serializer.save(realtor=realtor)
        apartment.save()
