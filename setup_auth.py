#!/usr/bin/env python3
"""
Google Calendar OAuth Setup Script
Run this outside the container to generate token.json
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Scopes for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'data/token.json'

def setup_authentication():
    """Setup Google Calendar authentication and save token"""
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found!")
        print("Please download credentials.json from Google Cloud Console")
        return False
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    creds = None
    # Check if token already exists and is valid
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                print("Starting new authentication flow...")
                os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            print("Starting OAuth flow...")
            print("A browser window will open for authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Token saved to {TOKEN_FILE}")
    else:
        print("✅ Valid token already exists")
    
    return True

if __name__ == '__main__':
    print("Google Calendar MCP Authentication Setup")
    print("=" * 50)
    
    if setup_authentication():
        print("\n✅ Authentication setup complete!")
        print("You can now use the Google Calendar MCP server.")
    else:
        print("\n❌ Authentication setup failed!")
        print("Please check your credentials.json file.")