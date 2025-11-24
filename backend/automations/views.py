from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Automation, Keyword, Trigger, Listener, Post
from .serializers import (
    AutomationListSerializer,
    AutomationDetailSerializer,
    KeywordSerializer,
    TriggerSerializer,
    ListenerSerializer,
    PostSerializer
)


class AutomationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Automation CRUD operations.
    Replaces your automation server actions.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AutomationListSerializer
        return AutomationDetailSerializer
    
    def get_queryset(self):
        # Only return automations for the current user
        return Automation.objects.filter(user=self.request.user).prefetch_related(
            'keywords', 'trigger', 'posts', 'listener'
        )
    
    def create(self, request):
        """Create a new automation - replaces createAutomations()"""
        automation = Automation.objects.create(
            user=request.user,
            name=request.data.get('name', 'Untitled'),
            id=request.data.get('id', None)  # Optional custom ID
        )
        serializer = AutomationDetailSerializer(automation)
        return Response({
            'status': 200,
            'data': 'Automation created',
            'res': serializer.data
        }, status=status.HTTP_200_OK)
    
    def list(self, request):
        """Get all automations - replaces getAllAutomations()"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 200,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """Get single automation - replaces getAutomationInfo()"""
        automation = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = AutomationDetailSerializer(automation)
        return Response({
            'status': 200,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        """Update automation - replaces updateAutomationName()"""
        automation = get_object_or_404(self.get_queryset(), pk=pk)
        
        if 'name' in request.data:
            automation.name = request.data['name']
        if 'active' in request.data:
            automation.active = request.data['active']
        
        automation.save()
        
        return Response({
            'status': 200,
            'data': 'Automation successfully updated'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate/deactivate automation - replaces activateAutomation()"""
        automation = get_object_or_404(self.get_queryset(), pk=pk)
        active_state = request.data.get('state', False)
        automation.active = active_state
        automation.save()
        
        return Response({
            'status': 200,
            'data': f"Automation {'activated' if active_state else 'disabled'}"
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def add_listener(self, request, pk=None):
        """Add listener to automation - replaces saveListener()"""
        automation = get_object_or_404(self.get_queryset(), pk=pk)
        
        listener_type = request.data.get('listener', 'MESSAGE')
        prompt = request.data.get('prompt', '')
        reply = request.data.get('reply', '')
        
        Listener.objects.update_or_create(
            automation=automation,
            defaults={
                'listener': listener_type,
                'prompt': prompt,
                'comment_reply': reply
            }
        )
        
        return Response({
            'status': 200,
            'data': 'Listener created'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def add_trigger(self, request, pk=None):
        """Add triggers to automation - replaces saveTrigger()"""
        automation = get_object_or_404(self.get_queryset(), pk=pk)
        triggers = request.data.get('trigger', [])
        
        # Clear existing triggers
        automation.trigger.all().delete()
        
        # Add new triggers
        for trigger_type in triggers:
            Trigger.objects.create(
                automation=automation,
                type=trigger_type
            )
        
        return Response({
            'status': 200,
            'data': 'Trigger saved'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def add_keyword(self, request, pk=None):
        """Add keyword to automation - replaces saveKeyword()"""
        automation = get_object_or_404(self.get_queryset(), pk=pk)
        keyword = request.data.get('keyword', '')
        
        if not keyword:
            return Response({
                'status': 400,
                'data': 'Keyword is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            Keyword.objects.create(
                automation=automation,
                word=keyword
            )
            return Response({
                'status': 200,
                'data': 'Keyword added successfully'
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'status': 404,
                'data': 'Cannot add this keyword'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def add_posts(self, request, pk=None):
        """Add posts to automation - replaces savePosts()"""
        automation = get_object_or_404(self.get_queryset(), pk=pk)
        posts = request.data.get('posts', [])
        
        for post_data in posts:
            Post.objects.create(
                automation=automation,
                postid=post_data['postid'],
                caption=post_data.get('caption'),
                media=post_data['media'],
                media_type=post_data['mediaType']
            )
        
        return Response({
            'status': 200,
            'data': 'Posts attached'
        }, status=status.HTTP_200_OK)


class KeywordViewSet(viewsets.ModelViewSet):
    """ViewSet for Keyword operations"""
    serializer_class = KeywordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Keyword.objects.filter(automation__user=self.request.user)
    
    def destroy(self, request, pk=None):
        """Delete keyword - replaces deleteKeyword()"""
        keyword = get_object_or_404(self.get_queryset(), pk=pk)
        keyword.delete()
        return Response({
            'status': 200,
            'data': 'Keyword deleted'
        }, status=status.HTTP_200_OK)