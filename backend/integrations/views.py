from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Integration
from automations.serializers import IntegrationSerializer
from datetime import datetime, timedelta, timezone
import requests
from django.conf import settings


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_integrations(request):
    """
    Get user's integrations.
    Replaces getIntegration() from your Next.js app.
    """
    integrations = Integration.objects.filter(
        user=request.user,
        name='INSTAGRAM'
    )
    serializer = IntegrationSerializer(integrations, many=True)
    
    return Response({
        'status': 200,
        'integrations': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def integrate_instagram(request):
    """
    Handle Instagram OAuth integration.
    Replaces onIntegrate() from your Next.js app.
    """
    code = request.data.get('code')
    
    if not code:
        return Response({
            'status': 400,
            'data': 'Authorization code required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already has an integration
    existing_integration = Integration.objects.filter(user=request.user).first()
    
    if existing_integration:
        return Response({
            'status': 404,
            'data': 'Integration already exists'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Exchange code for access token
    token_data = generate_instagram_tokens(code)
    
    if not token_data:
        return Response({
            'status': 401,
            'data': 'Failed to get access token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get Instagram user ID
    try:
        insta_response = requests.get(
            f"{settings.INSTAGRAM_BASE_URL}/me",
            params={
                'fields': 'user_id',
                'access_token': token_data['access_token']
            }
        )
        insta_data = insta_response.json()
        instagram_user_id = insta_data.get('user_id')
        
        # Create integration
        expires_at = datetime.now(timezone.utc) + timedelta(days=60)
        
        integration = Integration.objects.create(
            user=request.user,
            name='INSTAGRAM',
            token=token_data['access_token'],
            expires_at=expires_at,
            instagram_id=instagram_user_id
        )
        
        return Response({
            'status': 200,
            'data': {
                'firstname': request.user.firstname,
                'lastname': request.user.lastname
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 500,
            'data': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_posts(request):
    """
    Get Instagram posts for the user.
    Replaces getProfilePosts() from your Next.js app.
    """
    try:
        integration = Integration.objects.filter(
            user=request.user,
            name='INSTAGRAM'
        ).first()
        
        if not integration:
            return Response({
                'status': 404,
                'data': 'No Instagram integration found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch posts from Instagram API
        response = requests.get(
            f"{settings.INSTAGRAM_BASE_URL}/me/media",
            params={
                'fields': 'id,caption,media_url,media_type,timestamp',
                'limit': 10,
                'access_token': integration.token
            }
        )
        
        posts_data = response.json()
        
        return Response({
            'status': 200,
            'data': posts_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 500,
            'data': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_instagram_tokens(code):
    """
    Helper function to exchange authorization code for access token.
    Similar to generateTokens() from your fetch.ts file.
    """
    try:
        # This is a placeholder - implement based on your Instagram OAuth flow
        # You'll need to make a POST request to Instagram's token endpoint
        response = requests.post(
            'https://api.instagram.com/oauth/access_token',
            data={
                'client_id': settings.INSTAGRAM_CLIENT_ID,
                'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': settings.INSTAGRAM_REDIRECT_URI,
                'code': code
            }
        )
        return response.json()
    except Exception as e:
        print(f"Token generation error: {str(e)}")
        return None