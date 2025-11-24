import uuid
from django.db import models
from accounts.models import User

class Automation(models.Model):
    """Automation model - matches Prisma Automation schema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='Untitled')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automations')
    
    class Meta:
        db_table = 'Automation'
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.name} - {self.user.email}"


class Trigger(models.Model):
    """Trigger model - matches Prisma Trigger schema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50)  # 'COMMENT' or 'DM'
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='trigger')
    
    class Meta:
        db_table = 'Trigger'
        
    def __str__(self):
        return f"{self.type} - {self.automation.name}"


class Keyword(models.Model):
    """Keyword model - matches Prisma Keyword schema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=255)
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='keywords')
    
    class Meta:
        db_table = 'Keyword'
        unique_together = ('automation', 'word')  # Ensures unique keyword per automation
        
    def __str__(self):
        return f"{self.word} - {self.automation.name}"


class Listener(models.Model):
    """Listener model - matches Prisma Listener schema"""
    LISTENER_CHOICES = [
        ('SMARTAI', 'Smart AI'),
        ('MESSAGE', 'Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.OneToOneField(Automation, on_delete=models.CASCADE, related_name='listener')
    listener = models.CharField(max_length=10, choices=LISTENER_CHOICES, default='MESSAGE')
    prompt = models.TextField()
    comment_reply = models.TextField(null=True, blank=True)
    dm_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'Listener'
        
    def __str__(self):
        return f"{self.listener} - {self.automation.name}"


class Post(models.Model):
    """Post model - matches Prisma Post schema"""
    MEDIA_TYPE_CHOICES = [
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('CAROSEL_ALBUM', 'Carousel Album'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    postid = models.CharField(max_length=255)
    caption = models.TextField(null=True, blank=True)
    media = models.TextField()
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='IMAGE')
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='posts')
    
    class Meta:
        db_table = 'Post'
        
    def __str__(self):
        return f"{self.postid} - {self.automation.name}"


class DM(models.Model):
    """DM model - matches Prisma Dms schema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='dms')
    created_at = models.DateTimeField(auto_now_add=True)
    sender_id = models.CharField(max_length=255, null=True, blank=True)
    reciever = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'Dms'
        ordering = ['created_at']
        
    def __str__(self):
        return f"DM {self.id} - {self.automation.name}"