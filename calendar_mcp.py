from mcp.server.fastmcp import FastMCP
from dateutil import parser, tz  # Added for flexible date-time parsing
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import os



# Scopes for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# ----------------------------
# Helper: Google Calendar Service
# ----------------------------

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                os.remove(TOKEN_FILE)
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# ----------------------------
# Helper: Date Parsing
# ----------------------------
def parse_datetime(user_input: str, timezone: str = 'Asia/Karachi') -> str:
    """
    Parse a free-form datetime string, attach/convert to the given zone,
    and return an RFC3339 string with offset (e.g. '2025-05-20T15:00:00+05:00').
    """
    if not user_input:
        return None

    # 1) Parse into a datetime (might be naive or have another zone)
    dt = parser.parse(user_input, dayfirst=False, yearfirst=True)

    # 2) Force-set missing tzinfo, or convert to target zone
    target_tz = tz.gettz(timezone)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=target_tz)
    else:
        dt = dt.astimezone(target_tz)

    # 3) Return full ISO with offset
    return dt.isoformat()



# -----------------------------
# MCP Server & Tool Definitions
# -----------------------------
mcp = FastMCP("Google Calendar MCP Server")


# List Events Tool
@mcp.tool(name="list_upcoming_events", description="List upcoming calendar events with optional max results")
def list_upcoming_events(max_results: int = 10) -> list:
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=max_results, singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    return events



# Add Event Tool
@mcp.tool(name="add_new_event", description="Add a new calendar event and return its ID")
def add_new_event(summary: str, description: str = "", start_datetime_str: str = None,
                   end_datetime_str: str = None, timezone: str = 'Asia/Karachi',
                   location: str = '') -> str:
    service = get_calendar_service()
    start_dt = parse_datetime(start_datetime_str, timezone)
    end_dt = parse_datetime(end_datetime_str, timezone)
    body = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {'dateTime': start_dt, 'timeZone': timezone},
        'end': {'dateTime': end_dt, 'timeZone': timezone},
    }
    event = service.events().insert(calendarId='primary', body=body).execute()

    # Print event details
    summary = event.get('summary', 'No Title')
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    timezone = event['start'].get('timeZone', 'Unknown Timezone')
    description = event.get('description', 'No Description')
    location = event.get('location', 'No Location')

    print(f"**Name:** {summary}")
    print(f"**Date:** {datetime.datetime.fromisoformat(start).strftime('%B %d, %Y')}")
    print(f"**Time:** {datetime.datetime.fromisoformat(start).strftime('%H:%M')} - {datetime.datetime.fromisoformat(end).strftime('%H:%M')} ({timezone})")
    print(f"**Description:** {description}")
    print(f"**Location:** {location}")
    print("#" * 50)
    print("This event has been Added successfully!")
    print("#" * 50)
    print(f"Event ID: {event['id']}")

    return event['id']




# Update Event Tool: match by name or ID, or list current month events
@mcp.tool(name="update_event", description="Update an event by ID or name; lists current month if no identifier given")
def update_event(event_id: str = None, name: str = None,
                 new_summary: str = None, new_description: str = None,
                 new_start: str = None, new_end: str = None,
                 new_location: str = None,
                 timezone: str = 'Asia/Karachi') -> any:
    service = get_calendar_service()
    # If no ID or name provided: list this month's events
    if not event_id and not name:
        now = datetime.datetime.utcnow()
        start_month = now.replace(day=1).isoformat() + 'Z'
        next_month = (now.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        end_month = next_month.isoformat() + 'Z'
        events = service.events().list(
            calendarId='primary', timeMin=start_month, timeMax=end_month,
            singleEvents=True, orderBy='startTime'
        ).execute().get('items', [])
        return events
    # Resolve name to ID if needed
    if not event_id and name:
        # fetch current month and find match
        this_month = update_event(name=None)  # recursive to list events
        matches = [e for e in this_month if e.get('summary', '').lower() == name.lower()]
        if not matches:
            raise ValueError(f"No event found with name '{name}'")
        event = matches[0]
    else:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
    # Apply updates
    if new_summary: event['summary'] = new_summary
    if new_description: event['description'] = new_description
    if new_start:
        event['start']['dateTime'] = parse_datetime(new_start, timezone)
        event['start']['timeZone'] = timezone
    if new_end:
        event['end']['dateTime'] = parse_datetime(new_end, timezone)
        event['end']['timeZone'] = timezone
    if new_location: event['location'] = new_location

    updated = service.events().update(
        calendarId='primary', eventId=event['id'], body=event
    ).execute()

    # Print updated event details
    summary = updated.get('summary', 'No Title')
    start = updated['start'].get('dateTime', updated['start'].get('date'))
    end = updated['end'].get('dateTime', updated['end'].get('date'))
    timezone = updated['start'].get('timeZone', 'Unknown Timezone')
    description = updated.get('description', 'No Description')
    location = updated.get('location', 'No Location')

    print(f"** New Name:** {summary}")
    print(f"**New Date:** {datetime.datetime.fromisoformat(start).strftime('%B %d, %Y')}")
    print(f"**New Time:** {datetime.datetime.fromisoformat(start).strftime('%H:%M')} - {datetime.datetime.fromisoformat(end).strftime('%H:%M')} ({timezone})")
    print(f"**New Description:** {description}")
    print(f"**New location:** {location}")
    print("#" * 50)
    print("This event has been updated successfully!")
    print("#" * 50)

    return {'id': updated['id'], 'summary': updated.get('summary')}




# Delete Event Tool: match by name or ID, or list current month events
@mcp.tool(name="delete_event", description="Delete an event by ID or name; lists current month if no identifier given")
def delete_event(event_id: str = None, name: str = None) -> any:
    service = get_calendar_service()
    if not event_id and not name:
        return update_event()  # lists current month
    if not event_id and name:
        events = delete_event()  # list
        matches = [e for e in events if e.get('summary', '').lower() == name.lower()]
        if not matches:
            raise ValueError(f"No event found with name '{name}'")
        event = matches[0]
        event_id = event['id']
    else:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()

    # Print event details before deletion
    summary = event.get('summary', 'No Title')
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    timezone = event['start'].get('timeZone', 'Unknown Timezone')
    description = event.get('description', 'No Description')
    location = event.get('location', 'No Location')

    print(f"**Name:** {summary}")
    print(f"**Date:** {datetime.datetime.fromisoformat(start).strftime('%B %d, %Y')}")
    print(f"**Time:** {datetime.datetime.fromisoformat(start).strftime('%H:%M')} - {datetime.datetime.fromisoformat(end).strftime('%H:%M')} ({timezone})")
    print(f"**Description:** {description}")
    print(f"**Location:** {location}")
    print("#" * 50)
    print("This event has been deleted successfully!")
    print("#" * 50)

    # Delete the event
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return {'deleted': True, 'id': event_id}

# -----------------------------
# Server Entry Point
# -----------------------------


@mcp.tool()
def manage_calendar(action: str,
                    event_id: str = None,
                    summary: str = None,
                    description: str = None,
                    location: str = None,
                    start_datetime_str: str = None,
                    end_datetime_str: str = None,
                    timezone: str = 'Asia/Karachi',
                    max_results: int = 10) -> any:
    """
    General entrypoint to manage calendar via action parameter:
    - 'list'      -> list_upcoming_events
    - 'add'       -> add_new_event
    - 'update'    -> update_existing_event
    - 'delete'    -> delete_event_by_id
    """
    if action == 'list':
        return list_upcoming_events(max_results)
    elif action == 'add':
        return add_new_event(summary, description, start_datetime_str, end_datetime_str, timezone, location)
    elif action == 'update':
        return update_event(event_id, summary, description, start_datetime_str, end_datetime_str, timezone, location)
    elif action == 'delete':
        return delete_event(event_id)
    else:
        raise ValueError(f"Unknown action '{action}'. Use 'list', 'add', 'update', or 'delete'.")

# -----------------------------
# Server Entry Point
# -----------------------------
# Run this MCP server; the 'manage_calendar' tool can replace CLI logic.
if __name__ == '__main__':
    mcp.run(transport="sse")
