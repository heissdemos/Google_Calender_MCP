#!/usr/bin/env python3
"""
Google Calendar OAuth Setup Script (Manual/Headless)
Run this to generate token.json without browser requirement
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
    """Setup Google Calendar authentication using manual flow"""
    
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
            print("Starting OAuth flow (manual mode)...")
            print("=" * 50)
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            
            # Use console-based flow instead of browser
            try:
                # Try to get authorization URL manually
                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                print("Please follow these steps:")
                print("1. Open this URL in your browser:")
                print(f"   {auth_url}")
                print("2. Complete the authorization flow")
                print("3. Copy the authorization code from the browser")
                print()
                
                code = input("Enter the authorization code: ").strip()
                
                if not code:
                    print("No code entered. Aborting.")
                    return False
                
                flow.fetch_token(code=code)
                creds = flow.credentials
                
            except Exception as e:
                print(f"Manual flow failed: {e}")
                print("Trying alternative method...")
                
                # Fallback: use run_console if available
                try:
                    creds = flow.run_console()
                except Exception as e2:
                    print(f"Console flow also failed: {e2}")
                    return False
        
        # Save the credentials for the next run
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            print(f"✅ Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"Error saving token: {e}")
            return False
    else:
        print("✅ Valid token already exists")
    
    return True

if __name__ == '__main__':
    print("Google Calendar MCP Authentication Setup (Manual)")
    print("=" * 60)
    
    if setup_authentication():
        print("\n✅ Authentication setup complete!")
        print("You can now use the Google Calendar MCP server.")
    else:
        print("\n❌ Authentication setup failed!")
        print("Please check your credentials.json file.")