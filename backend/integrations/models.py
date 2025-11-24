import uuid
from django.db import models
from accounts.models import User

class Integration(models.Model):
    """Integration model - matches Prisma Integrations schema"""
    INTEGRATION_CHOICES = [
        ('INSTAGRAM', 'Instagram'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, choices=INTEGRATION_CHOICES, default='INSTAGRAM')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integrations')
    token = models.TextField(unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    instagram_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    class Meta:
        db_table = 'Integrations'
        
    def __str__(self):
        return f"{self.user.email} - {self.name}"