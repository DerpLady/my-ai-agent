# My AI Agent

An AI-powered Gmail assistant with a Chrome extension interface. Uses LangChain/LangGraph to interact with Gmail and Google Calendar via natural language.

## Features

- **Summarize emails** - Get quick summaries of recent inbox messages
- **Send emails** - Compose and send emails through natural language
- **Check calendar** - View upcoming calendar events
- **Chrome extension** - Chat interface directly in Gmail

## Project Structure

```
├── gmail_agent.py      # Main agent with Gmail/Calendar tools (Flask server)
├── simple_agent.py     # Basic example agent with calculator tool
└── my-extension/
    ├── content.js      # Chrome extension content script
    └── manifest.json   # Extension manifest
```

## Setup

### 1. Install Dependencies

```bash
pip install flask flask-cors python-dotenv langchain langchain-openai langgraph google-auth google-auth-oauthlib google-api-python-client
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Gmail API** and **Google Calendar API**
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `credentials.json` in the root directory

### 4. Run the Agent Server

```bash
python gmail_agent.py
```

On first run, a browser window will open for Google OAuth authorization. After authorizing, a `token.json` file will be created.

### 5. Install Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `my-extension` folder

### 6. Use the Agent

1. Open [Gmail](https://mail.google.com)
2. Click the robot button in the bottom-right corner
3. Type commands like:
   - "Summarize my recent emails"
   - "What's on my calendar this week?"
   - "Send an email to example@email.com about the meeting"

## Simple Agent Example

`simple_agent.py` is a minimal example showing how to create a LangChain agent with a calculator tool:

```bash
python simple_agent.py
```

## Security Notes

- Never commit `.env`, `credentials.json`, or `token.json` to version control
- These files are included in `.gitignore`
