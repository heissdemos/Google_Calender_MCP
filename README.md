# 📅 **Google Calendar MCP**

Welcome to the **Google Calendar MCP** project! 🚀

Easily manage your Google Calendar events (list, add, update, delete) using a powerful Multi-Component Protocol (MCP) server and agent system. This project is designed for seamless integration, automation, and user-friendliness.

---

## ✨ **What This MCP Server Can Do**

- 🔍 **List** all your upcoming Google Calendar events
- ➕ **Add** new events with custom details
- ✏️ **Update** existing events by name or ID
- 🗑️ **Delete** events from your calendar
- 🛡️ Secure authentication with Google OAuth
- 🖥️ Easy-to-use CLI interface for all operations

---

## 🛠️ **Getting Started**

### 1. **Create Google Cloud Project & Credentials**

1. **Create a New Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Click on the project dropdown at the top of the page
   - Click "New Project"
   - Enter a project name (e.g., "My Calendar App")
   - Click "Create"

2. **Enable Google Calendar API**
   - In the left sidebar, click on "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on "Google Calendar API" in the results
   - Click "Enable"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Select "External" user type
   - Fill in the required information:
     - App name
     - User support email
     - Developer contact information
   - Click "Save and Continue"
   - Under "Scopes", click "Add or Remove Scopes"
   - Add these scopes:
     ```
     https://www.googleapis.com/auth/calendar
     https://www.googleapis.com/auth/calendar.events
     ```
   - Click "Save and Continue"
   - Under "Test users", click "Add Users"
   - Add your email address and any other test users
   - Click "Save and Continue"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as the application type
   - Name your OAuth client (e.g., "Calendar Desktop Client")
   - Click "Create"
   - Click "Download JSON" to save your credentials
   - Rename the downloaded file to `credentials.json`
- **Place `credentials.json` in your project root directory**

---

## ⚙️ **Setup & Installation**

### 2. **Create and Activate a Virtual Environment**

#### **macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### **Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. **Install Dependencies**

```bash
uv sync
```

---

## 🚦 **Running the Project**

### 4. **Start the Calendar MCP Server**

```bash
python calendar_mcp.py
```

### 5. **Open a New Terminal and Start the Calendar Server**

```bash
python calendar_server.py
```

---

## 🔑 **First Time Authentication**

- When you use a tool (e.g., list events) for the first time, a browser window will open.
- Log in with your Google account and grant access.
- A `token.json` file will be created in your root directory for future access.

---

## 📝 **Usage Example**

- Use the CLI to interact with your calendar.
- Example: **List all upcoming events**
- The agent will prompt you, and you can type commands like:
  - `List all my upcoming events`
  - `Add a meeting tomorrow at 3pm called 'Team Sync'`
  - `Update the event 'Team Sync' to 4pm`
  - `Delete the event 'Team Sync'`

You can now **list, add, update, and delete** all your Google Calendar events easily! 🎉

---

## 👨‍💻 **Developer**

Made with ❤️ by [KhurramDevOps](https://github.com/KhurramDevOps)

---

> _Feel free to contribute, open issues, or star the repo!_
