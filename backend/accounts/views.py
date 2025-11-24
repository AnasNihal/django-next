from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import User, Subscription
from automations.serializers import UserSerializer, SubscriptionSerializer
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@permission_classes([AllowAny])
def onboard_user(request):
    """
    Onboard a new user or return existing user.
    Replaces onBoardUser() from your Next.js app.
    """
    clerk_user_id = request.data.get('clerkId')
    email = request.data.get('email')
    firstname = request.data.get('firstname')
    lastname = request.data.get('lastname')
    
    if not clerk_user_id or not email:
        return Response({
            'status': 400,
            'data': 'Missing required fields'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user exists
    try:
        user = User.objects.get(clerk_id=clerk_user_id)
        
        # Check if integration token needs refresh (similar to your code)
        integrations = user.integrations.all()
        if integrations.exists():
            integration = integrations.first()
            from datetime import datetime, timezone
            
            if integration.expires_at:
                days_left = (integration.expires_at - datetime.now(timezone.utc)).days
                
                if days_left < 5:
                    # Refresh token logic here
                    from integrations.utils import refresh_instagram_token
                    new_token = refresh_instagram_token(integration.token)
                    if new_token:
                        from datetime import timedelta
                        integration.token = new_token['access_token']
                        integration.expires_at = datetime.now(timezone.utc) + timedelta(days=60)
                        integration.save()
        
        return Response({
            'status': 200,
            'data': {
                'firstname': user.firstname,
                'lastname': user.lastname
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create(
            clerk_id=clerk_user_id,
            email=email,
            firstname=firstname,
            lastname=lastname
        )
        
        # Create subscription
        Subscription.objects.create(user=user, plan='FREE')
        
        return Response({
            'status': 200,
            'data': {
                'slug': user.clerk_id
            }
        }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """
    Get current user information.
    Replaces onUserInfo() from your Next.js app.
    """
    serializer = UserSerializer(request.user)
    return Response({
        'status': 200,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe(request):
    """
    Handle subscription after Stripe checkout.
    Replaces onSubscribe() from your Next.js app.
    """
    session_id = request.data.get('session_id')
    
    if not session_id:
        return Response({
            'status': 400,
            'data': 'Missing session_id'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Retrieve the Stripe session
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session:
            # Update user subscription
            subscription = request.user.subscription
            subscription.customer_id = session.customer
            subscription.plan = 'PRO'
            subscription.save()
            
            return Response({
                'status': 200,
                'data': 'Subscription updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 404,
            'data': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'status': 500,
            'data': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def create_stripe_session(request):
    """
    Create a Stripe checkout session.
    Replaces the /api/payment endpoint.
    """
    try:
        price_id = settings.STRIPE_SUBSCRIPTION_PRICE_ID
        
        session = stripe.checkout.Session.create(
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            success_url=f"{settings.FRONTEND_URL}/payment?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/payment?cancel=true",
        )
        
        return Response({
            'status': 200,
            'session_url': session.url
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 400,
            'data': f'Error: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)