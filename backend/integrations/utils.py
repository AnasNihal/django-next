import requests
from django.conf import settings


def refresh_instagram_token(token):
    """
    Refresh an Instagram access token.
    Similar to refreshToken() from your fetch.ts file.
    """
    try:
        response = requests.get(
            'https://graph.instagram.com/refresh_access_token',
            params={
                'grant_type': 'ig_refresh_token',
                'access_token': token
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Token refresh failed: {response.text}')
            return None
            
    except Exception as e:
        print(f'Token refresh error: {str(e)}')
        return None


def send_dm(page_id, recipient_id, message, token):
    """
    Send a direct message to an Instagram user.
    Similar to sendDM() from your fetch.ts file.
    """
    try:
        url = f"https://graph.facebook.com/v21.0/{page_id}/messages"
        
        response = requests.post(
            url,
            json={
                'recipient': {'id': recipient_id},
                'message': {'text': message}
            },
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        return {
            'status': 200 if response.status_code == 200 else 400,
            'data': response.json()
        }
        
    except Exception as e:
        print(f'DM send error: {str(e)}')
        return {
            'status': 500,
            'data': str(e)
        }


def send_private_reply_to_comment(page_id, comment_id, message, token):
    """
    Send a private reply to an Instagram comment.
    Similar to sendPrivateReplyToComment() from your fetch.ts file.
    """
    try:
        url = f"https://graph.facebook.com/v21.0/{page_id}/messages"
        
        response = requests.post(
            url,
            json={
                'recipient': {'comment_id': comment_id},
                'message': {'text': message}
            },
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        return {
            'status': 200 if response.status_code == 200 else 400,
            'data': response.json()
        }
        
    except Exception as e:
        print(f'Private reply error: {str(e)}')
        return {
            'status': 500,
            'data': str(e)
        }


def get_comment_details(comment_id, token):
    """
    Get details about a specific Instagram comment.
    Similar to getCommentDetails() from your fetch.ts file.
    """
    try:
        url = f"https://graph.facebook.com/v21.0/{comment_id}"
        
        response = requests.get(
            url,
            params={
                'fields': 'id,text,from,timestamp',
                'access_token': token
            }
        )
        
        return response.json() if response.status_code == 200 else None
        
    except Exception as e:
        print(f'Get comment error: {str(e)}')
        return None