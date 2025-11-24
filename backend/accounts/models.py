import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """User model - matches Prisma User schema"""

    username = None 

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clerk_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    
    class Meta:
        db_table = 'User'
        
    def __str__(self):
        return f"{self.email} ({self.clerk_id})"


class Subscription(models.Model):
    """Subscription model - matches Prisma Subscription schema"""
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    created_at = models.DateTimeField(auto_now_add=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='FREE')
    updated_at = models.DateTimeField(auto_now=True)
    customer_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    class Meta:
        db_table = 'Subscription'
        
    def __str__(self):
        return f"{self.user.email} - {self.plan}"