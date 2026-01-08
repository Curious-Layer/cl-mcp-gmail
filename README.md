# Gmail MCP Server

A Model Context Protocol (MCP) server that provides access to Gmail API endpoints.

## Features

This MCP server provides the following Gmail operations:

### Profile & Account
- **get_profile**: Get Gmail profile information

### Message Operations
- **get_message**: Get specific message details
- **send_message**: Send an email
- **send_message_with_attachment**: Send email with file attachments
- **reply_to_message**: Reply to an existing email
- **search_messages**: Search messages using Gmail query syntax
- **delete_message**: Permanently delete a message
- **trash_message**: Move message to trash
- **untrash_message**: Restore message from trash
- **mark_as_read**: Mark message as read
- **mark_as_unread**: Mark message as unread

### Thread Operations
- **get_thread**: Get entire email thread

### Label Operations
- **list_labels**: Get all labels
- **create_label**: Create new label
- **delete_label**: Delete a label
- **modify_message_labels**: Add/remove labels from a message

### Draft Operations
- **list_drafts**: List draft messages
- **create_draft**: Create a draft message

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google OAuth

You need to create OAuth credentials with the following scopes:
- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.compose`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.labels`

Each tool requires an `oauth_token` parameter, which is a JSON string containing your access token and other necessary details. The `_get_token_data` function in the server script shows the expected format. It is recommended to use a separate script to handle the OAuth 2.0 flow to generate this token data.

### 3. Configure Your MCP Client

The server can be run in different transport modes.

**stdio (default)**:
```bash
python gmail_mcp_server.py
```

**SSE (Server-Sent Events)**:
```bash
python gmail_mcp_server.py --transport sse --host 127.0.0.1 --port 8080
```

**Streamable HTTP**:
```bash
python gmail_mcp_server.py --transport streamable-http --host 127.0.0.1 --port 8080
```

## Usage Examples

### Get Profile
```json
{
  "tool": "get_profile",
  "arguments": {
    "oauth_token": "{\"token\": \"...\", \"refresh_token\": \"...\", ...}"
  }
}
```

### Search Messages
```json
{
  "tool": "search_messages",
  "arguments": {
    "oauth_token": "{\"token\": \"...\", \"refresh_token\": \"...\", ...}",
    "query": "is:inbox is:unread",
    "max_results": 10
  }
}
```

### Send Email
```json
{
  "tool": "send_message",
  "arguments": {
    "oauth_token": "{\"token\": \"...\", \"refresh_token\": \"...\", ...}",
    "to": "recipient@example.com",
    "subject": "Hello from MCP",
    "body": "This is a test email sent via the Gmail MCP server."
  }
}
```

## Gmail Search Query Syntax

Common search operators for `search_messages`:

- `from:sender@example.com` - From specific sender
- `to:recipient@example.com` - To specific recipient
- `subject:keyword` - Subject contains keyword
- `has:attachment` - Has attachments
- `is:unread` - Unread messages
- `is:starred` - Starred messages
- `after:2024/01/01` - After date
- `before:2024/12/31` - Before date
- `larger:10M` - Larger than 10MB
- `filename:pdf` - Specific file type

## Troubleshooting

### Authentication Issues
If you get authentication errors, ensure your `oauth_token` is valid and has not expired. You may need to refresh it.

### Permission Denied
Make sure your OAuth credentials have the correct scopes enabled in the Google Cloud Console.

### Rate Limits
The Gmail API has usage quotas. If you exceed them, you'll get quota errors. Check your quota usage in the Google Cloud Console.

## Security Notes

- Keep your OAuth credentials and tokens secure and do not commit them to version control.
- All operations are performed with the authenticated user's permissions.
- Be careful with delete operations - they are permanent.

## Logging
The server logs operations to the console (stdout/stderr). To enable logging to a file, you can modify the `handlers` in `gmail_mcp_server.py`.