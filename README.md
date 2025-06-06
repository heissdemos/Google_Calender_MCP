# 📅 **Google Calendar MCP Server**

A powerful Google Calendar Multi-Component Protocol (MCP) server for seamless integration with Claude and other MCP-compatible clients. Manage your Google Calendar events through a containerized, secure, and easy-to-use MCP server.

---

## ✨ **Features**

- 🔍 **List upcoming calendar events** with customizable limits
- ➕ **Create new events** with flexible date/time parsing
- ✏️ **Update existing events** by ID or name
- 🗑️ **Delete events** from your calendar
- 🛡️ **Secure OAuth 2.0 authentication** with Google
- 🐳 **Dockerized deployment** for consistent environments
- 📡 **MCP stdio transport** for Claude integration
- 💾 **Persistent token storage** for seamless re-authentication

---

## 🛠️ **Quick Start**

### Prerequisites

- Docker installed on your system
- Google Cloud Project with Calendar API enabled
- Claude Code CLI (optional, for direct integration)

### 1. **Clone and Setup**

```bash
git clone <repository-url>
cd Google_Calender_MCP
```

### 2. **Google Cloud Setup**

#### Create Google Cloud Project & Credentials

1. **Create a New Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Click "New Project" and enter a name (e.g., "Calendar MCP")
   - Click "Create"

2. **Enable Google Calendar API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Select "External" user type
   - Fill in required information:
     - App name: "Calendar MCP"
     - User support email
     - Developer contact information
   - Add scopes:
     ```
     https://www.googleapis.com/auth/calendar
     https://www.googleapis.com/auth/calendar.events
     ```
   - Add your email as a test user

4. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application"
   - Name it "Calendar MCP Client"
   - Download the JSON file and rename it to `credentials.json`
   - **Place `credentials.json` in the project root directory**

### 3. **Build the Docker Container**

```bash
docker build -t google-calendar-mcp .
```

### 4. **Authentication Setup**

Since the MCP server runs in a container without browser access, authentication is done manually:

#### Generate OAuth URL

```bash
docker run --rm -i \
    -v "$(pwd):/app" \
    -v "$(pwd)/data:/app/data" \
    -e TOKEN_FILE=/app/data/token.json \
    google-calendar-mcp \
    uv run python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
auth_url, _ = flow.authorization_url(prompt='consent')
print('Please visit this URL to authorize this application:')
print(auth_url)
print()
print('After authorization, you will get a code. Use it with the next command.')
"
```

#### Complete Authentication

1. **Open the generated URL** in your browser
2. **Sign in** with your Google account
3. **Grant permission** to access your calendar
4. **Copy the authorization code** from the browser
5. **Save the token** using the code:

```bash
docker run --rm -i \
    -v "$(pwd):/app" \
    -v "$(pwd)/data:/app/data" \
    -e TOKEN_FILE=/app/data/token.json \
    google-calendar-mcp \
    uv run python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
import os
code = 'YOUR_AUTHORIZATION_CODE_HERE'
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/calendar'])
flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
flow.fetch_token(code=code)
os.makedirs('data', exist_ok=True)
with open('/app/data/token.json', 'w') as f:
    f.write(flow.credentials.to_json())
print('✅ Token saved successfully!')
"
```

Replace `YOUR_AUTHORIZATION_CODE_HERE` with the actual code from step 4.

### 5. **Integration with Claude**

#### Add to Claude MCP Configuration

```bash
claude mcp add google-calendar /path/to/Google_Calender_MCP/google-calendar-mcp-wrapper.sh
```

#### Manual Testing

```bash
# Test the MCP server directly
./google-calendar-mcp-wrapper.sh
```

---

## 🔧 **Available MCP Tools**

### **list_upcoming_events**
List your upcoming calendar events.
```
Parameters:
- max_results (optional, default: 10) - Number of events to return
```

### **add_new_event**
Create a new calendar event.
```
Parameters:
- summary (required) - Event title
- description (optional) - Event description
- start_datetime_str (required) - Start time (e.g., "2025-06-10 15:00")
- end_datetime_str (required) - End time (e.g., "2025-06-10 16:00")
- timezone (optional, default: "Asia/Karachi") - Timezone
- location (optional) - Event location
```

### **update_event**
Update an existing calendar event.
```
Parameters:
- event_id (optional) - Google Calendar event ID OR
- name (optional) - Event name to search for
- new_summary (optional) - New event title
- new_description (optional) - New description
- new_start (optional) - New start time
- new_end (optional) - New end time
- new_location (optional) - New location
- timezone (optional, default: "Asia/Karachi") - Timezone
```

### **delete_event**
Delete a calendar event.
```
Parameters:
- event_id (optional) - Google Calendar event ID OR
- name (optional) - Event name to search for
```

### **manage_calendar**
Universal calendar management tool.
```
Parameters:
- action (required) - "list", "add", "update", or "delete"
- + all parameters from the respective individual tools
```

---

## 💬 **Usage Examples**

Once integrated with Claude, you can ask:

- **"Liste meine nächsten 5 Termine"**
- **"Erstelle einen Termin für morgen 14:00 - Meeting mit Team"**
- **"Zeige alle Termine für heute"**
- **"Ändere meinen Termin 'Zahnarzt' auf 16:00"**
- **"Lösche den Termin 'Team Meeting'"**

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│     Claude      │    │   MCP Server         │    │   Google Calendar   │
│                 │    │   (Docker)           │    │   API               │
│                 │◄──►│                      │◄──►│                     │
│                 │    │  - calendar_mcp.py   │    │  - OAuth 2.0        │
│                 │    │  - FastMCP           │    │  - REST API         │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
        │                         │
        │              ┌──────────────────────┐
        └──────────────┤   stdio transport    │
                       │   wrapper script     │
                       └──────────────────────┘
```

## 📁 **Project Structure**

```
Google_Calender_MCP/
├── calendar_mcp.py              # Main MCP server
├── run_with_claude.py          # Claude integration wrapper
├── setup_auth_manual.py        # Manual authentication script
├── google-calendar-mcp-wrapper.sh  # MCP wrapper script
├── credentials.json            # Google OAuth credentials (you provide)
├── data/
│   └── token.json             # OAuth token (auto-generated)
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Container orchestration
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

---

## 🔒 **Security Notes**

- **Never commit `credentials.json`** to version control
- **Never commit `data/token.json`** to version control
- The `.gitignore` file excludes these sensitive files
- Tokens are stored persistently in the `data/` directory
- OAuth tokens automatically refresh when expired

---

## 🐛 **Troubleshooting**

### Authentication Issues
```bash
# Check if token exists and is valid
ls -la data/token.json

# Re-run authentication if needed
rm data/token.json
# Then follow authentication steps again
```

### Container Issues
```bash
# Rebuild container
docker build -t google-calendar-mcp .

# Check container logs
docker logs google-calendar-mcp

# Test container manually
docker run --rm -it google-calendar-mcp /bin/bash
```

### MCP Integration Issues
```bash
# Test wrapper script
./google-calendar-mcp-wrapper.sh

# Check Claude MCP configuration
claude mcp list

# Debug MCP communication
echo '{"method": "tools/list"}' | ./google-calendar-mcp-wrapper.sh
```

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 **Acknowledgments**

- FastMCP framework for MCP server implementation
- Google Calendar API for calendar integration
- Docker for containerization
- Claude for MCP client integration

---

> 💡 **Need help?** Open an issue or check the troubleshooting section above.