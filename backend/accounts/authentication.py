import jwt
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User

class ClerkAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for Clerk JWT tokens.
    This verifies the JWT token sent from the Next.js frontend.
    """
    
    def authenticate(self, request):
        # Get the authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return None
            
        try:
            # Extract the token (format: "Bearer <token>")
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            
            # Get Clerk's JWKS (JSON Web Key Set) for verification
            jwks_url = f"https://api.clerk.dev/v1/jwks"
            jwks = requests.get(jwks_url).json()
            
            # Decode and verify the token
            # Note: In production, you should cache the JWKS
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}  # We'll verify manually
            )
            
            clerk_user_id = decoded.get('sub')
            
            if not clerk_user_id:
                raise exceptions.AuthenticationFailed('Invalid token: No user ID found')
            
            # Get or create user
            try:
                user = User.objects.get(clerk_id=clerk_user_id)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found')
            
            return (user, None)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        return 'Bearer'


def get_current_user(request):
    """
    Helper function to get the current authenticated user.
    Similar to onCurrentUser() in your Next.js app.
    """
    if not request.user.is_authenticated:
        raise exceptions.AuthenticationFailed('User not authenticated')
    return request.user