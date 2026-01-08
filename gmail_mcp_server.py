#!/usr/bin/env python3
"""
MCP Server for Gmail API
Provides access to Gmail operations through Model Context Protocol
"""

import json
import logging
import os
import argparse
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List
from pathlib import Path

from fastmcp import FastMCP
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.labels",
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # logging.FileHandler('gmail_mcp_server.log'),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger("gmail-mcp-server")

# Create FastMCP instance
mcp = FastMCP("CL Gmail MCP Server")

# Global service instance
# We don't need this for Stateless Functioning
_service = None


def _get_token_data(token_data: str) -> Dict:
    """Decode access token JSON string to dictionary"""
    try:
        token_data = json.loads(token_data)
        auth_data = {
            "token": token_data.get("token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": token_data.get("client_id"),
            "client_secret": token_data.get("client_secret"),
            "scopes": token_data.get("scopes"),
        }
        return auth_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode access token: {e}")
        return {}


def _get_service(token_data: str):
    """Create Gmail service with provided access token"""
    auth_data = _get_token_data(token_data)
    logger.info("Creating Gmail API service with provided access token")
    # Don't pass scopes - the token already has its authorized scopes
    creds = Credentials(**auth_data)
    service = build("gmail", "v1", credentials=creds)
    logger.info("Gmail API service created successfully")
    return service


# Define MCP Tools


@mcp.tool(name="get_profile", description="Get the user's Gmail profile information")
def get_profile(oauth_token: str) -> Dict:
    """Get Gmail profile"""
    logger.info("Executing get_profile")
    try:
        service = _get_service(oauth_token)

        profile = service.users().getProfile(userId="me").execute()

        logger.info(f"Retrieved profile for: {profile.get('emailAddress')}")
        return profile
    except Exception as e:
        logger.error(f"Error in get_profile: {e}")
        return {"error": str(e)}


@mcp.tool(
    name="get_message", description="Get a specific message by ID with full details"
)
def get_message(oauth_token: str, message_id: str, format: str = "full") -> Dict:
    """Get message details"""
    logger.info(f"Executing get_message for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format=format)
            .execute()
        )

        logger.info("Retrieved message details")
        return message
    except Exception as e:
        logger.error(f"Error in get_message: {e}")
        return {"error": str(e)}


@mcp.tool(name="send_message", description="Send an email message")
def send_message(
    oauth_token: str, to: str, subject: str, body: str, cc: str = "", bcc: str = ""
) -> Dict:
    """Send an email"""
    logger.info(f"Executing send_message to: {to}")
    try:
        service = _get_service(oauth_token)

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )

        logger.info(f"Message sent successfully: {send_message.get('id')}")
        return {
            "message": "Email sent successfully",
            "id": send_message.get("id"),
            "threadId": send_message.get("threadId"),
        }
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return {"error": str(e)}


@mcp.tool(
    name="send_message_with_attachment",
    description="Send an email message with file attachments",
)
def send_message_with_attachment(
    oauth_token: str,
    to: str,
    subject: str,
    body: str,
    attachment_path: str,
    cc: str = "",
) -> Dict:
    """Send email with attachment"""
    logger.info(f"Executing send_message_with_attachment to: {to}")
    try:
        service = _get_service(oauth_token)

        message = MIMEMultipart()
        message["to"] = to
        message["subject"] = subject

        if cc:
            message["cc"] = cc

        message.attach(MIMEText(body, "plain"))

        # Attach file
        if os.path.exists(attachment_path):
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition", f"attachment; filename= {filename}"
                )
                message.attach(part)
        else:
            return {"error": f"Attachment file not found: {attachment_path}"}

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )

        logger.info(
            f"Message with attachment sent successfully: {send_message.get('id')}"
        )
        return {
            "message": "Email with attachment sent successfully",
            "id": send_message.get("id"),
            "threadId": send_message.get("threadId"),
        }
    except Exception as e:
        logger.error(f"Error in send_message_with_attachment: {e}")
        return {"error": str(e)}


@mcp.tool(name="reply_to_message", description="Reply to an existing email message")
def reply_to_message(oauth_token: str, message_id: str, body: str) -> Dict:
    """Reply to a message"""
    logger.info(f"Executing reply_to_message for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        # Get original message to extract headers
        original_message = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["Subject", "From", "To", "Message-ID"],
            )
            .execute()
        )

        headers = {
            h["name"]: h["value"] for h in original_message["payload"]["headers"]
        }
        thread_id = original_message["threadId"]

        # Create reply
        message = MIMEText(body)
        message["to"] = headers.get("From", "")
        message["subject"] = "Re: " + headers.get("Subject", "").replace("Re: ", "")
        message["In-Reply-To"] = headers.get("Message-ID", "")
        message["References"] = headers.get("Message-ID", "")

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message, "threadId": thread_id})
            .execute()
        )

        logger.info(f"Reply sent successfully: {send_message.get('id')}")
        return {
            "message": "Reply sent successfully",
            "id": send_message.get("id"),
            "threadId": send_message.get("threadId"),
        }
    except Exception as e:
        logger.error(f"Error in reply_to_message: {e}")
        return {"error": str(e)}


@mcp.tool(name="delete_message", description="Delete a message permanently")
def delete_message(oauth_token: str, message_id: str) -> Dict:
    """Delete a message"""
    logger.info(f"Executing delete_message for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        service.users().messages().delete(userId="me", id=message_id).execute()

        logger.info("Message deleted successfully")
        return {"message": f"Message {message_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error in delete_message: {e}")
        return {"error": str(e)}


@mcp.tool(name="trash_message", description="Move a message to trash")
def trash_message(oauth_token: str, message_id: str) -> Dict:
    """Trash a message"""
    logger.info(f"Executing trash_message for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        message = service.users().messages().trash(userId="me", id=message_id).execute()

        logger.info("Message moved to trash")
        return {
            "message": "Message moved to trash successfully",
            "id": message.get("id"),
        }
    except Exception as e:
        logger.error(f"Error in trash_message: {e}")
        return {"error": str(e)}


@mcp.tool(name="untrash_message", description="Remove a message from trash")
def untrash_message(oauth_token: str, message_id: str) -> Dict:
    """Untrash a message"""
    logger.info(f"Executing untrash_message for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        message = (
            service.users().messages().untrash(userId="me", id=message_id).execute()
        )

        logger.info("Message removed from trash")
        return {
            "message": "Message removed from trash successfully",
            "id": message.get("id"),
        }
    except Exception as e:
        logger.error(f"Error in untrash_message: {e}")
        return {"error": str(e)}


@mcp.tool(
    name="modify_message_labels", description="Add or remove labels from a message"
)
def modify_message_labels(
    oauth_token: str,
    message_id: str,
    add_labels: List[str] = [],
    remove_labels: List[str] = [],
) -> Dict:
    """Modify message labels"""
    logger.info(f"Executing modify_message_labels for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        body = {}
        if add_labels:
            body["addLabelIds"] = add_labels
        if remove_labels:
            body["removeLabelIds"] = remove_labels

        message = (
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body=body)
            .execute()
        )

        logger.info("Message labels modified successfully")
        return {
            "message": "Labels modified successfully",
            "id": message.get("id"),
            "labelIds": message.get("labelIds"),
        }
    except Exception as e:
        logger.error(f"Error in modify_message_labels: {e}")
        return {"error": str(e)}


@mcp.tool(name="list_labels", description="Get all labels in the user's mailbox")
def list_labels(
    oauth_token: str,
) -> Dict:
    """List all labels"""
    logger.info("Executing list_labels")
    try:
        service = _get_service(oauth_token)

        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        logger.info(f"Found {len(labels)} labels")
        return {"count": len(labels), "labels": labels}
    except Exception as e:
        logger.error(f"Error in list_labels: {e}")
        return {"error": str(e)}


@mcp.tool(name="create_label", description="Create a new label")
def create_label(
    oauth_token: str,
    name: str,
    label_list_visibility: str = "labelShow",
    message_list_visibility: str = "show",
) -> Dict:
    """Create a new label"""
    logger.info(f"Executing create_label: {name}")
    try:
        service = _get_service(oauth_token)

        label = {
            "name": name,
            "labelListVisibility": label_list_visibility,
            "messageListVisibility": message_list_visibility,
        }

        created_label = (
            service.users().labels().create(userId="me", body=label).execute()
        )

        logger.info(f"Label created successfully: {created_label.get('id')}")
        return {"message": "Label created successfully", "label": created_label}
    except Exception as e:
        logger.error(f"Error in create_label: {e}")
        return {"error": str(e)}


@mcp.tool(name="delete_label", description="Delete a label")
def delete_label(oauth_token: str, label_id: str) -> Dict:
    """Delete a label"""
    logger.info(f"Executing delete_label for ID: {label_id}")
    try:
        service = _get_service(oauth_token)

        service.users().labels().delete(userId="me", id=label_id).execute()

        logger.info("Label deleted successfully")
        return {"message": f"Label {label_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error in delete_label: {e}")
        return {"error": str(e)}


@mcp.tool(
    name="search_messages", description="Search messages using Gmail search syntax"
)
def search_messages(oauth_token: str, query: str, max_results: int = 10) -> Dict:
    """Search messages with Gmail query syntax"""
    logger.info(f"Executing search_messages with query: {query}")
    try:
        service = _get_service(oauth_token)

        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=min(max_results, 500))
            .execute()
        )

        messages = results.get("messages", [])

        logger.info(f"Search found {len(messages)} messages")
        return {
            "count": len(messages),
            "messages": messages,
            "resultSizeEstimate": results.get("resultSizeEstimate"),
        }
    except Exception as e:
        logger.error(f"Error in search_messages: {e}")
        return {"error": str(e)}


@mcp.tool(name="mark_as_read", description="Mark a message as read")
def mark_as_read(oauth_token: str, message_id: str) -> Dict:
    """Mark message as read"""
    logger.info(f"Executing mark_as_read for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        message = (
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]})
            .execute()
        )

        logger.info("Message marked as read")
        return {
            "message": "Message marked as read successfully",
            "id": message.get("id"),
        }
    except Exception as e:
        logger.error(f"Error in mark_as_read: {e}")
        return {"error": str(e)}


@mcp.tool(name="mark_as_unread", description="Mark a message as unread")
def mark_as_unread(oauth_token: str, message_id: str) -> Dict:
    """Mark message as unread"""
    logger.info(f"Executing mark_as_unread for ID: {message_id}")
    try:
        service = _get_service(oauth_token)

        message = (
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"addLabelIds": ["UNREAD"]})
            .execute()
        )

        logger.info("Message marked as unread")
        return {
            "message": "Message marked as unread successfully",
            "id": message.get("id"),
        }
    except Exception as e:
        logger.error(f"Error in mark_as_unread: {e}")
        return {"error": str(e)}


@mcp.tool(name="get_thread", description="Get an entire email thread")
def get_thread(oauth_token: str, thread_id: str, format: str = "full") -> Dict:
    """Get email thread"""
    logger.info(f"Executing get_thread for ID: {thread_id}")
    try:
        service = _get_service(oauth_token)

        thread = (
            service.users()
            .threads()
            .get(userId="me", id=thread_id, format=format)
            .execute()
        )

        logger.info(f"Retrieved thread with {len(thread.get('messages', []))} messages")
        return thread
    except Exception as e:
        logger.error(f"Error in get_thread: {e}")
        return {"error": str(e)}


@mcp.tool(name="list_drafts", description="List draft messages")
def list_drafts(oauth_token: str, max_results: int = 10) -> Dict:
    """List drafts"""
    logger.info("Executing list_drafts")
    try:
        service = _get_service(oauth_token)

        results = (
            service.users()
            .drafts()
            .list(userId="me", maxResults=min(max_results, 500))
            .execute()
        )

        drafts = results.get("drafts", [])

        logger.info(f"Found {len(drafts)} drafts")
        return {"count": len(drafts), "drafts": drafts}
    except Exception as e:
        logger.error(f"Error in list_drafts: {e}")
        return {"error": str(e)}


@mcp.tool(name="create_draft", description="Create a draft message")
def create_draft(oauth_token: str, to: str, subject: str, body: str) -> Dict:
    """Create a draft"""
    logger.info(f"Executing create_draft to: {to}")
    try:
        service = _get_service(oauth_token)

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        draft = (
            service.users()
            .drafts()
            .create(userId="me", body={"message": {"raw": raw_message}})
            .execute()
        )

        logger.info(f"Draft created successfully: {draft.get('id')}")
        return {"message": "Draft created successfully", "id": draft.get("id")}
    except Exception as e:
        logger.error(f"Error in create_draft: {e}")
        return {"error": str(e)}


# Function for parsing the cmd-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Gmail MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        help="Transport method for MCP (Allowed Values: 'stdio', 'sse', or 'streamable-http')",
        default=None,
    )
    parser.add_argument("--host", help="Host to bind the server to", default=None)
    parser.add_argument(
        "--port", type=int, help="Port to bind the server to", default=None
    )
    return parser.parse_args()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Gmail MCP Server Starting")
    logger.info("=" * 60)

    args = parse_args()

    # Build kwargs for mcp.run() only with provided values
    run_kwargs = {}
    if args.transport:
        run_kwargs["transport"] = args.transport
        logger.info(f"Transport: {args.transport}")
    if args.host:
        run_kwargs["host"] = args.host
        logger.info(f"Host: {args.host}")
    if args.port:
        run_kwargs["port"] = args.port
        logger.info(f"Port: {args.port}")

    try:
        # Start the MCP server with optional transport/host/port
        mcp.run(**run_kwargs)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        raise
