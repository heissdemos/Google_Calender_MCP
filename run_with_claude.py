#!/usr/bin/env python3
"""
Google Calendar MCP Server for Claude Integration
This script runs the authentication flow and starts the MCP server
"""

import sys
import os
from calendar_mcp import mcp, get_calendar_service
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.json')

def setup_authentication():
    """Setup Google Calendar authentication"""
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found!", file=sys.stderr)
        print("Please place credentials.json in the container", file=sys.stderr)
        return False
    
    creds = None
    # Check if token already exists and is valid
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading existing token: {e}", file=sys.stderr)
    
    # If there are no (valid) credentials available, create a mock token for demo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refreshing expired token...", file=sys.stderr)
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}", file=sys.stderr)
                return False
        else:
            print("No valid credentials found. Creating demo mode...", file=sys.stderr)
            # For demo purposes, we'll create a message about authentication
            return False
        
        # Save the refreshed credentials
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            print(f"Token saved to {TOKEN_FILE}", file=sys.stderr)
        except Exception as e:
            print(f"Error saving token: {e}", file=sys.stderr)
            return False
    
    return True

def run_mcp_server():
    """Run the MCP server with authentication check"""
    
    # Check if we have valid authentication
    auth_ok = setup_authentication()
    
    if not auth_ok:
        print("Authentication required. Please run setup outside container first.", file=sys.stderr)
    
    # Start the MCP server regardless (it will handle auth errors gracefully)
    print("Starting Google Calendar MCP Server...", file=sys.stderr)
    mcp.run(transport="stdio")

if __name__ == '__main__':
    run_mcp_server()