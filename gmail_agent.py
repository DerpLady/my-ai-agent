import os
import json
import base64
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

load_dotenv()
app = Flask(__name__)
CORS(app)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def get_gmail_service():
    """Handles the OAuth flow and returns the Gmail service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_calendar_service():
    """Handles the OAuth flow and returns the Calendar service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


# --- TOOLS ---

@tool
def summarize_emails(max_results: int = 5) -> str:
    """Use this to get a summary of recent emails in the inbox."""
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    if not messages:
        return "No recent emails found."

    summaries = []
    for msg in messages:
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From']
        ).execute()

        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown')
        snippet = message.get('snippet', '')

        summaries.append(f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n")

    return "\n---\n".join(summaries)


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Use this to send an email. Provide the recipient email address, subject, and body."""
    service = get_gmail_service()

    message = MIMEText(body)
    message['to'] = recipient
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        return f"Email sent successfully to {recipient}."
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@tool
def get_calendar_events(days_ahead: int = 7) -> str:
    """Use this to check calendar events. Returns events for the upcoming days."""
    service = get_calendar_service()

    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        return "No upcoming events found."

    event_summaries = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No title')
        event_summaries.append(f"- {summary} at {start}")

    count = len(events)
    return f"Total events: {count}\n\n" + "\n".join(event_summaries)


# --- AGENT STATE ---

class AgentState(TypedDict):
    """The state of the agent - tracks messages throughout the conversation."""
    messages: Annotated[list[BaseMessage], operator.add]


# --- AGENT GRAPH ---

tools = [summarize_emails, send_email, get_calendar_events]

llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState) -> dict:
    """The agent's reasoning step - decides what to do next."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Decide whether to continue to tools or end the conversation."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# Create the state graph
graph = StateGraph(AgentState)

# Add nodes: agent reasoning and tool execution
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

# Set the entry point
graph.set_entry_point("agent")

# Add edges: agent -> tools (conditional), tools -> agent
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

# Compile the graph
agent = graph.compile()


def run_agent(user_input: str) -> str:
    """Run the agent with a user query and return the response."""
    result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
    return result["messages"][-1].content


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    reply = run_agent(data.get('command'))
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(port=5000)
