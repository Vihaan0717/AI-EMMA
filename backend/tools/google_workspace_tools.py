import os
import logging
import time
import inspect
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage

logger = logging.getLogger("GoogleWorkspace")

# Scopes needed for Calendar and Gmail
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

# State file for authorization/approval cache
STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'google_workspace_state.json')

# Rate limit registry
_last_called = {}

def _check_rate_limit(action_name: str, min_interval: float = 15.0) -> tuple[bool, str]:
    """Check if the action is called too frequently."""
    now = time.time()
    last = _last_called.get(action_name, 0.0)
    elapsed = now - last
    if elapsed < min_interval:
        wait_time = int(min_interval - elapsed)
        return False, f"Rate limit hit for Google Workspace {action_name}. Please wait {wait_time}s."
    _last_called[action_name] = now
    return True, ""

def _is_explicit_or_needed(tool_name: str) -> bool:
    """Detects if the call is explicitly requested by the user or needed by system protocols (e.g. morning briefing)."""
    # 1. Check if there is an active temporary approval flag in the state file
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                approved_until = state.get("approved_until", 0.0)
                if time.time() < approved_until:
                    return True
    except Exception as e:
        logger.warning(f"Error reading workspace state file: {e}")

    # 2. Inspect call stack to see if it is called from morning briefing, user tests, or direct UI command routing
    for frame_info in inspect.stack():
        filename = frame_info.filename.lower()
        # Explicit calls from test scripts or direct CLI/UI commands
        if 'morning_briefing' in filename or 'test_google' in filename or 'live_test' in filename:
            return True
            
    # 3. Check if an autonomous agent is calling this in the background
    is_agent = False
    for frame_info in inspect.stack():
        filename = frame_info.filename.lower()
        if 'manager.py' in filename or 'fleet' in filename or 're_act' in filename or 'loop' in frame_info.function.lower():
            is_agent = True
            break
            
    return not is_agent

def set_workspace_approval(duration_seconds: int = 300):
    """Sets temporary approval for Google Workspace tools (default: 5 minutes)."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        state = {"approved_until": time.time() + duration_seconds}
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        logger.info(f"Workspace access approved for {duration_seconds}s.")
        return f"Google Workspace access approved for the next {duration_seconds // 60} minutes."
    except Exception as e:
        logger.error(f"Failed to write workspace approval state: {e}")
        return f"Failed to approve Workspace access: {e}"

def get_credentials():
    creds = None
    # Paths relative to project root
    token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'token.json')
    creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'credentials.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Missing {creds_path}. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return creds

async def get_daily_schedule():
    """Fetches today's events from Google Calendar."""
    # Check rate limit
    ok, err = _check_rate_limit("get_daily_schedule", min_interval=10.0)
    if not ok:
        return err

    # Check permission gate
    if not _is_explicit_or_needed("get_daily_schedule"):
        return "⚠️ APPROVAL REQUIRED: JARVIS is attempting to read your Calendar. Please type 'Approve Workspace' or 'Approve Gmail' to authorize."

    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        end_of_day = datetime.utcnow().replace(hour=23, minute=59, second=59).isoformat() + 'Z'
        
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              timeMax=end_of_day, maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return "You have no upcoming meetings today."
        
        schedule = "Here is your schedule for today:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            time_str = datetime.fromisoformat(start).strftime('%I:%M %p') if 'T' in start else "All Day"
            schedule += f"- {time_str}: {event['summary']}\n"
            
        return schedule
    except FileNotFoundError:
        return "Authentication required. I need the credentials.json file to access your calendar."
    except Exception as e:
        logger.error(f"Calendar error: {e}")
        return f"Failed to retrieve schedule: {e}"

async def read_unread_emails():
    """Fetches up to 5 unread emails from Gmail."""
    # Check rate limit
    ok, err = _check_rate_limit("read_unread_emails", min_interval=10.0)
    if not ok:
        return err

    # Check permission gate
    if not _is_explicit_or_needed("read_unread_emails"):
        return "⚠️ APPROVAL REQUIRED: JARVIS is attempting to read your Gmail. Please type 'Approve Workspace' or 'Approve Gmail' to authorize."

    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            return "You have no new unread emails."
            
        output = "Here are your latest unread emails:\n"
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
            output += f"- From: {sender} | Subject: {subject}\n"
            
        return output
    except FileNotFoundError:
        return "Authentication required. I need the credentials.json file to access your emails."
    except Exception as e:
        logger.error(f"Gmail error: {e}")
        return f"Failed to retrieve emails: {e}"

async def create_email_draft(to_address: str, subject: str, body: str):
    """Creates an email draft in Gmail."""
    # Check rate limit
    ok, err = _check_rate_limit("create_email_draft", min_interval=5.0)
    if not ok:
        return err

    # Check permission gate
    if not _is_explicit_or_needed("create_email_draft"):
        return "⚠️ APPROVAL REQUIRED: JARVIS is attempting to draft an email. Please type 'Approve Workspace' or 'Approve Gmail' to authorize."

    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_address
        message['From'] = 'me'
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'message': {'raw': encoded_message}}
        
        draft = service.users().drafts().create(userId='me', body=create_message).execute()
        return f"Draft created successfully. Draft ID: {draft['id']}"
    except FileNotFoundError:
        return "Authentication required. I need the credentials.json file to access your emails."
    except Exception as e:
        logger.error(f"Gmail draft error: {e}")
        return f"Failed to create draft: {e}"
