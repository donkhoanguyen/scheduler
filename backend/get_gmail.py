from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import base64
import os.path
import pickle
import json

def build_gmail_service():
    """Build and return Gmail API service with proper authentication
    Port: 8080 """
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None

    # Load existing token if present
    if os.path.exists('credentials/token.pickle'):
        with open('credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Refresh token if expired or create new if none exists
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/gg_credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
            
        # Save credentials for next run
        with open('credentials/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f'Failed to build service: {str(e)}')
        return None
    
def get_email_content(payload):
    """Extract email content from payload"""
    if 'parts' in payload:
        # Multipart message
        parts = payload.get('parts', [])
        content = ""
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    content += base64.urlsafe_b64decode(data).decode('utf-8')
        return content
    else:
        # Single part message
        data = payload.get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return ""

# Get emails from the last 8 hours
def get_emails_from_last_8_hours(service):

    eight_hours_ago = datetime.now() - timedelta(hours=8)
    timestamp = int(eight_hours_ago.timestamp())
    # Combine queries for incoming emails and time filter
    query = f"to:me -from:me AND after:{timestamp}"
    
    # Fetch emails
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
        from_addr = next((header['value'] for header in headers if header['name'] == 'From'), "No Sender")
        snippet = msg.get('snippet', '')
        content = get_email_content(payload)
        
        emails.append({
            'id': message['id'],
            'subject': subject,
            'from': from_addr,
            'snippet': snippet,
            'content': content
        })
    return emails

def save_emails(emails, base_dir="email_archive"):
    """Save emails to JSON files with directory structure"""
    try:
        # Create base directory if it doesn't exist
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        
        # Create dated subdirectory
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dir = os.path.join(base_dir, today)
        os.makedirs(daily_dir, exist_ok=True)
        
        # Save each email
        saved_count = 0
        for email in emails:
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{timestamp}_{email['id']}.json"
            filepath = os.path.join(daily_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(email, f, indent=2, ensure_ascii=False)
            saved_count += 1
            
        return f"Successfully saved {saved_count} emails to {daily_dir}"
    
    except Exception as e:
        return f"Error saving emails: {str(e)}"

def main():
    service = build_gmail_service()
    emails = get_emails_from_last_8_hours(service)
    result = save_emails(emails)
    print(result)

if __name__ == "__main__":
    main()