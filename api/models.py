from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class UserConfig(models.Model):
    USER_ROLE_CLIENT = 'CLIENT'
    USER_ROLE_REALTOR = 'REALTOR'
    USER_ROLE_ADMIN = 'ADMIN'

    USER_ROLE_CHOICES = (
        (USER_ROLE_CLIENT, 'Client'),
        (USER_ROLE_REALTOR, 'Realtor'),
        (USER_ROLE_ADMIN, 'Admin')
    )

    user = models.OneToOneField(User, related_name='config', on_delete=models.CASCADE)
    role = models.CharField(choices=USER_ROLE_CHOICES, max_length=10, default=USER_ROLE_CLIENT)

class Apartment(models.Model):
    APARTMENT_AVAILABLE = 'AVAILABLE'
    APARTMENT_RENTED = 'RENTED'

    APARTMENT_STATUS_CHOICES = (
        (APARTMENT_AVAILABLE, 'available'),
        (APARTMENT_RENTED, 'rented'),
    )

    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=300, default='', blank=True)
    size = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(100), MaxValueValidator(5000)])
    price = models.FloatField(null=False, blank=False, validators=[MinValueValidator(10), MaxValueValidator(10000)])
    rooms = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(1), MaxValueValidator(100)])
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False)
    address = models.CharField(max_length=300, default='Sudbury, Canada', null=False, blank=False)
    added_date = models.DateField(auto_now_add=True)
    status = models.CharField(choices=APARTMENT_STATUS_CHOICES, max_length=10, default=APARTMENT_AVAILABLE)
    realtor = models.ForeignKey(User, related_name='realtor', on_delete=models.CASCADE)
