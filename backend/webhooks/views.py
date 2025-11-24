from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status as http_status
from django.http import HttpResponse
from django.conf import settings
from automations.models import Automation, Keyword, DM
import requests
import openai
import json

# Configure OpenAI
openai.api_key = settings.OPENAI_API_KEY


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def instagram_webhook(request):
    """
    Handle Instagram webhooks for comments and DMs.
    Replaces your Next.js webhook route.
    """
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and token == settings.WEBHOOK_VERIFY_TOKEN:
            print('Webhook verified')
            return HttpResponse(challenge)
        
        return HttpResponse('Forbidden', status=403)
    
    # POST request - webhook event
    try:
        webhook_payload = json.loads(request.body)
        print('=== Webhook Received ===')
        print('Full Payload:', json.dumps(webhook_payload, indent=2))
        
        # Check if it's an Instagram webhook
        if webhook_payload.get('object') != 'instagram':
            return Response({'message': 'Not Instagram webhook'}, status=http_status.HTTP_200_OK)
        
        entry = webhook_payload.get('entry', [{}])[0]
        
        if not entry:
            return Response({'message': 'No entry data'}, status=http_status.HTTP_200_OK)
        
        # Handle COMMENTS
        if 'changes' in entry:
            return handle_comment_event(entry, webhook_payload)
        
        # Handle DIRECT MESSAGES
        if 'messaging' in entry:
            return handle_messaging_event(entry, webhook_payload)
        
        return Response({'message': 'Event processed'}, status=http_status.HTTP_200_OK)
        
    except Exception as e:
        print(f'Webhook Error: {str(e)}')
        return Response(
            {'message': 'Error processing webhook'},
            status=http_status.HTTP_200_OK  # Always return 200 to avoid Meta retry
        )


def handle_comment_event(entry, webhook_payload):
    """Handle comment events"""
    print('=== Processing Comment Event ===')
    
    change = entry.get('changes', [{}])[0]
    if not change or change.get('field') != 'comments':
        return Response({'message': 'Not a comment event'}, status=http_status.HTTP_200_OK)
    
    value = change.get('value', {})
    print('Comment Value:', json.dumps(value, indent=2))
    
    # Extract comment data
    comment_text = value.get('text', '')
    comment_id = value.get('id')
    media_id = value.get('media', {}).get('id')
    from_user_id = value.get('from', {}).get('id')
    page_id = entry.get('id')
    
    if not comment_text or not comment_id:
        print('Missing comment text or ID')
        return Response({'message': 'Invalid comment data'}, status=http_status.HTTP_200_OK)
    
    print(f'Comment Text: {comment_text}')
    print(f'Comment ID: {comment_id}')
    print(f'Media ID: {media_id}')
    print(f'From User ID: {from_user_id}')
    
    # Check if comment matches any keyword
    matched_keyword = match_keyword(comment_text)
    print(f'Keyword Match: {matched_keyword}')
    
    if not matched_keyword:
        print('No keyword match found')
        return Response({'message': 'No keyword match'}, status=http_status.HTTP_200_OK)
    
    # Get automation details
    automation = get_keyword_automation(matched_keyword.automation_id, is_dm=False)
    
    if not automation or not automation.trigger.filter(type='COMMENT').exists():
        print('No automation or trigger found')
        return Response({'message': 'No automation'}, status=http_status.HTTP_200_OK)
    
    # Check if this post is being monitored
    if media_id:
        is_monitored = automation.posts.filter(postid=media_id).exists()
        if not is_monitored:
            print('Post not in automation list')
            return Response({'message': 'Post not monitored'}, status=http_status.HTTP_200_OK)
    
    # Get access token
    integration = automation.user.integrations.filter(name='INSTAGRAM').first()
    if not integration:
        print('No access token found')
        return Response({'message': 'No token'}, status=http_status.HTTP_200_OK)
    
    token = settings.META_PAGE_ACCESS_TOKEN
    
    # Handle MESSAGE listener
    if automation.listener and automation.listener.listener == 'MESSAGE':
        print('Sending private reply to comment...')
        
        try:
            send_private_reply_to_comment(
                page_id,
                comment_id,
                automation.listener.prompt or 'Thank you for your comment!',
                token
            )
            
            # Track response
            automation.listener.comment_count += 1
            automation.listener.save()
            
            print('Private reply sent successfully')
            return Response({'message': 'Private reply sent'}, status=http_status.HTTP_200_OK)
            
        except Exception as e:
            print(f'Failed to send private reply: {str(e)}')
    
    # Handle SMARTAI listener
    if (automation.listener and 
        automation.listener.listener == 'SMARTAI' and 
        automation.user.subscription.plan == 'PRO'):
        
        print('Using Smart AI for response...')
        
        try:
            # Generate AI response
            response = openai.ChatCompletion.create(
                model='gpt-4o',
                messages=[
                    {
                        'role': 'system',
                        'content': f"{automation.listener.prompt}. Keep responses under 2 sentences."
                    },
                    {
                        'role': 'user',
                        'content': comment_text
                    }
                ]
            )
            
            ai_response = response.choices[0].message.content
            
            if ai_response:
                # Save chat history
                DM.objects.create(
                    automation=automation,
                    sender_id=page_id,
                    reciever=from_user_id,
                    message=comment_text
                )
                
                DM.objects.create(
                    automation=automation,
                    sender_id=page_id,
                    reciever=from_user_id,
                    message=ai_response
                )
                
                # Send private reply
                send_private_reply_to_comment(page_id, comment_id, ai_response, token)
                
                # Track response
                automation.listener.comment_count += 1
                automation.listener.save()
                
                print('AI private reply sent successfully')
                return Response({'message': 'AI reply sent'}, status=http_status.HTTP_200_OK)
                
        except Exception as e:
            print(f'Smart AI error: {str(e)}')
    
    return Response({'message': 'Comment processed'}, status=http_status.HTTP_200_OK)


def handle_messaging_event(entry, webhook_payload):
    """Handle direct message events"""
    print('=== Processing Messaging Event ===')
    
    messaging = entry.get('messaging', [{}])[0]
    if not messaging:
        return Response({'message': 'No messaging data'}, status=http_status.HTTP_200_OK)
    
    message_text = messaging.get('message', {}).get('text', '')
    sender_id = messaging.get('sender', {}).get('id')
    recipient_id = messaging.get('recipient', {}).get('id')
    page_id = entry.get('id')
    
    print(f'Message Text: {message_text}')
    print(f'Sender ID: {sender_id}')
    
    # Check for keyword match
    matched_keyword = match_keyword(message_text)
    
    if matched_keyword:
        automation = get_keyword_automation(matched_keyword.automation_id, is_dm=True)
        
        if not automation or not automation.trigger.filter(type='DM').exists():
            return Response({'message': 'No automation'}, status=http_status.HTTP_200_OK)
        
        integration = automation.user.integrations.filter(name='INSTAGRAM').first()
        if not integration:
            return Response({'message': 'No token'}, status=http_status.HTTP_200_OK)
        
        token = settings.META_PAGE_ACCESS_TOKEN
        
        # Handle MESSAGE listener
        if automation.listener and automation.listener.listener == 'MESSAGE':
            send_dm(
                page_id,
                sender_id,
                automation.listener.prompt or 'Thank you for your message!',
                token
            )
            
            automation.listener.dm_count += 1
            automation.listener.save()
            
            return Response({'message': 'DM sent'}, status=http_status.HTTP_200_OK)
        
        # Handle SMARTAI listener (similar to comment handling)
        if (automation.listener and 
            automation.listener.listener == 'SMARTAI' and 
            automation.user.subscription.plan == 'PRO'):
            
            # AI response generation code here (similar to comment handling)
            pass
    
    # Handle conversation continuation
    # Check chat history and continue conversation
    # Implementation similar to your Next.js code
    
    return Response({'message': 'Message processed'}, status=http_status.HTTP_200_OK)


# Helper functions

def match_keyword(text):
    """Match text against keywords"""
    try:
        return Keyword.objects.filter(word__iexact=text).first()
    except:
        return None


def get_keyword_automation(automation_id, is_dm=False):
    """Get automation with related data"""
    try:
        automation = Automation.objects.get(id=automation_id)
        return automation
    except Automation.DoesNotExist:
        return None


def send_private_reply_to_comment(page_id, comment_id, message, token):
    """Send a private reply to a comment"""
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
    
    return response


def send_dm(page_id, recipient_id, message, token):
    """Send a direct message"""
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
    
    return response