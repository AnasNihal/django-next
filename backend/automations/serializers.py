from rest_framework import serializers
from .models import Automation, Trigger, Keyword, Listener, Post, DM
from accounts.models import User, Subscription
from integrations.models import Integration


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['id', 'word', 'automation']
        read_only_fields = ['id']


class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = ['id', 'type', 'automation']
        read_only_fields = ['id']


class ListenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listener
        fields = ['id', 'listener', 'prompt', 'comment_reply', 'dm_count', 'comment_count']
        read_only_fields = ['id', 'dm_count', 'comment_count']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'postid', 'caption', 'media', 'media_type', 'automation']
        read_only_fields = ['id']


class DMSerializer(serializers.ModelSerializer):
    class Meta:
        model = DM
        fields = ['id', 'created_at', 'sender_id', 'reciever', 'message']
        read_only_fields = ['id', 'created_at']


class AutomationListSerializer(serializers.ModelSerializer):
    """Serializer for listing automations"""
    keywords = KeywordSerializer(many=True, read_only=True)
    listener = ListenerSerializer(read_only=True)
    
    class Meta:
        model = Automation
        fields = ['id', 'name', 'created_at', 'active', 'keywords', 'listener']
        read_only_fields = ['id', 'created_at']


class AutomationDetailSerializer(serializers.ModelSerializer):
    """Serializer for automation details"""
    keywords = KeywordSerializer(many=True, read_only=True)
    trigger = TriggerSerializer(many=True, read_only=True)
    posts = PostSerializer(many=True, read_only=True)
    listener = ListenerSerializer(read_only=True)
    
    class Meta:
        model = Automation
        fields = ['id', 'name', 'created_at', 'active', 'keywords', 'trigger', 'posts', 'listener']
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'created_at', 'updated_at', 'customer_id']
        read_only_fields = ['id', 'created_at', 'updated_at']


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = ['id', 'name', 'token', 'expires_at', 'instagram_id']
        read_only_fields = ['id']
        extra_kwargs = {'token': {'write_only': True}}  # Don't expose token in responses


class UserSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)
    integrations = IntegrationSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'clerk_id', 'email', 'firstname', 'lastname', 'created_at', 'subscription', 'integrations']
        read_only_fields = ['id', 'created_at']