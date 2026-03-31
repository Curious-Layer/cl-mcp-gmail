**Manage Gmail inbox, send emails, and organize messages via API.**

A Model Context Protocol (MCP) server that exposes Gmail's API for comprehensive email management, including sending, receiving, searching, and organizing messages.

---

## Overview

The Gmail MCP Server provides stateless, multi-user access to Gmail's core operations:

- **Message Management** — Send, receive, retrieve, delete, and organize email messages
- **Email Organization** — Create labels, manage message labels, and organize inbox efficiently
- **Search & Filtering** — Advanced message search using Gmail search syntax
- **Draft & Thread Management** — Create drafts, manage email threads, and track read/unread status

Perfect for:

- Automated email workflow automation and processing
- Building AI-powered email management systems
- Integrating email capabilities into multi-agent applications

---

## Tools

<details>
<summary><code>get_profile</code> — Get the user's Gmail profile information</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object with Gmail scopes

**Output:**

```json
{
  "result": {
    "emailAddress": "user@gmail.com",
    "messagesTotal": 1234,
    "threadsTotal": 456,
    "historyId": "123456789"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/get_profile

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
  }
}
```

</details>

---

<details>
<summary><code>get_message</code> — Get a specific message by ID with full details</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to retrieve
- `format` (string, optional) — Response format: "full", "minimal", or "raw" (default: "full")

**Output:**

```json
{
  "result": {
    "id": "msg-123456",
    "threadId": "thread-789",
    "labelIds": ["INBOX", "UNREAD"],
    "snippet": "Email preview text...",
    "payload": {
      "headers": [
        { "name": "From", "value": "sender@example.com" },
        { "name": "To", "value": "user@gmail.com" },
        { "name": "Subject", "value": "Email Subject" }
      ],
      "body": { "data": "base64-encoded-body" }
    }
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/get_message

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
  },
  "message_id": "msg-123456",
  "format": "full"
}
```

</details>

---

<details>
<summary><code>send_message</code> — Send an email message</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `to` (string, required) — Recipient email address
- `subject` (string, required) — Email subject line
- `body` (string, required) — Email body content
- `cc` (string, optional) — CC recipients (comma-separated, default: "")
- `bcc` (string, optional) — BCC recipients (comma-separated, default: "")

**Output:**

```json
{
  "result": {
    "message": "Email sent successfully",
    "id": "msg-789123",
    "threadId": "thread-456"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/send_message

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.send"]
  },
  "to": "recipient@example.com",
  "subject": "Meeting Confirmation",
  "body": "Hi, please confirm your attendance at the meeting.",
  "cc": "manager@example.com"
}
```

</details>

---

<details>
<summary><code>send_message_with_attachment</code> — Send an email message with file attachments</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `to` (string, required) — Recipient email address
- `subject` (string, required) — Email subject line
- `body` (string, required) — Email body content
- `attachment_path` (string, required) — Local file path to attach
- `cc` (string, optional) — CC recipients (comma-separated, default: "")

**Output:**

```json
{
  "result": {
    "message": "Email with attachment sent successfully",
    "id": "msg-987654",
    "threadId": "thread-321"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/send_message_with_attachment

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.send"]
  },
  "to": "recipient@example.com",
  "subject": "Project Report",
  "body": "Please find the report attached.",
  "attachment_path": "/home/user/reports/Q1_report.pdf"
}
```

</details>

---

<details>
<summary><code>reply_to_message</code> — Reply to an existing email message</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to reply to
- `body` (string, required) — Reply body content

**Output:**

```json
{
  "result": {
    "message": "Reply sent successfully",
    "id": "msg-555444",
    "threadId": "thread-456"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/reply_to_message

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.send"]
  },
  "message_id": "msg-123456",
  "body": "Thanks for your message. I agree with your proposal."
}
```

</details>

---

<details>
<summary><code>delete_message</code> — Delete a message permanently</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to delete

**Output:**

```json
{
  "result": {
    "message": "Message deleted permanently",
    "id": "msg-123456"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/delete_message

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "message_id": "msg-123456"
}
```

</details>

---

<details>
<summary><code>trash_message</code> — Move a message to trash</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to trash

**Output:**

```json
{
  "result": {
    "message": "Message moved to trash",
    "id": "msg-123456"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/trash_message

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "message_id": "msg-123456"
}
```

</details>

---

<details>
<summary><code>untrash_message</code> — Remove a message from trash</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to restore

**Output:**

```json
{
  "result": {
    "message": "Message restored from trash",
    "id": "msg-123456"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/untrash_message

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "message_id": "msg-123456"
}
```

</details>

---

<details>
<summary><code>modify_message_labels</code> — Add or remove labels from a message</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to modify
- `add_labels` (array, optional) — Label IDs to add (default: [])
- `remove_labels` (array, optional) — Label IDs to remove (default: [])

**Output:**

```json
{
  "result": {
    "message": "Message labels updated",
    "id": "msg-123456",
    "labelIds": ["INBOX", "STARRED", "LABEL_1"]
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/modify_message_labels

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "message_id": "msg-123456",
  "add_labels": ["LABEL_1"],
  "remove_labels": ["UNREAD"]
}
```

</details>

---

<details>
<summary><code>list_labels</code> — Get all labels in the user's mailbox</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object

**Output:**

```json
{
  "result": {
    "count": 5,
    "labels": [
      { "id": "INBOX", "name": "INBOX", "type": "system" },
      { "id": "LABEL_1", "name": "Work", "type": "user" },
      { "id": "LABEL_2", "name": "Personal", "type": "user" }
    ]
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/list_labels

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
  }
}
```

</details>

---

<details>
<summary><code>create_label</code> — Create a new label</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `name` (string, required) — Label name
- `label_list_visibility` (string, optional) — Label visibility in list (default: "labelShow")
- `message_list_visibility` (string, optional) — Label visibility in messages (default: "show")

**Output:**

```json
{
  "result": {
    "message": "Label created successfully",
    "label": {
      "id": "LABEL_3",
      "name": "Projects",
      "type": "user"
    }
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/create_label

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "name": "Projects",
  "label_list_visibility": "labelShow",
  "message_list_visibility": "show"
}
```

</details>

---

<details>
<summary><code>delete_label</code> — Delete a label</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `label_id` (string, required) — The label ID to delete

**Output:**

```json
{
  "result": {
    "message": "Label deleted successfully",
    "id": "LABEL_3"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/delete_label

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "label_id": "LABEL_3"
}
```

</details>

---

<details>
<summary><code>search_messages</code> — Search messages using Gmail search syntax</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `query` (string, required) — Gmail search query (e.g., "from:sender@example.com is:unread")
- `max_results` (integer, optional) — Maximum results to return (default: 10)

**Output:**

```json
{
  "result": {
    "count": 3,
    "messages": [
      { "id": "msg-111", "threadId": "thread-1" },
      { "id": "msg-222", "threadId": "thread-2" }
    ],
    "resultSizeEstimate": 15
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/search_messages

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
  },
  "query": "is:unread from:manager@company.com",
  "max_results": 10
}
```

</details>

---

<details>
<summary><code>mark_as_read</code> — Mark a message as read</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to mark as read

**Output:**

```json
{
  "result": {
    "message": "Message marked as read",
    "id": "msg-123456"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/mark_as_read

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "message_id": "msg-123456"
}
```

</details>

---

<details>
<summary><code>mark_as_unread</code> — Mark a message as unread</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `message_id` (string, required) — The message ID to mark as unread

**Output:**

```json
{
  "result": {
    "message": "Message marked as unread",
    "id": "msg-123456"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/mark_as_unread

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
  },
  "message_id": "msg-123456"
}
```

</details>

---

<details>
<summary><code>get_thread</code> — Get an entire email thread</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `thread_id` (string, required) — The thread ID to retrieve
- `format` (string, optional) — Response format: "full", "minimal", or "raw" (default: "full")

**Output:**

```json
{
  "result": {
    "id": "thread-456",
    "historyId": "987654321",
    "messages": [
      { "id": "msg-111", "snippet": "First message..." },
      { "id": "msg-222", "snippet": "Reply message..." }
    ]
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/get_thread

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
  },
  "thread_id": "thread-456",
  "format": "full"
}
```

</details>

---

<details>
<summary><code>list_drafts</code> — List draft messages</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `max_results` (integer, optional) — Maximum drafts to return (default: 10)

**Output:**

```json
{
  "result": {
    "count": 2,
    "drafts": [
      { "id": "draft-1", "message": { "id": "msg-001" } },
      { "id": "draft-2", "message": { "id": "msg-002" } }
    ]
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/list_drafts

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
  },
  "max_results": 10
}
```

</details>

---

<details>
<summary><code>create_draft</code> — Create a draft message</summary>

**Inputs:**

- `oauth_token` (object, required) — Valid Google OAuth token object
- `to` (string, required) — Recipient email address
- `subject` (string, required) — Email subject line
- `body` (string, required) — Email body content

**Output:**

```json
{
  "result": {
    "message": "Draft created successfully",
    "id": "draft-3"
  }
}
```

**Usage Example:**

```bash
POST /mcp/cl-gmail/create_draft

{
  "oauth_token": {
    "token": "ya29.a0AfH6SMxxxxxxxxxxxxxx",
    "refresh_token": "1//0xxxxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxxxx",
    "scopes": ["https://www.googleapis.com/auth/gmail.compose"]
  },
  "to": "recipient@example.com",
  "subject": "Follow-up Meeting",
  "body": "Hi, please let me know your availability for next week."
}

```

</details>

---

## Reference & Support

<details>
<summary><strong>API Parameters Reference</strong></summary>

### Search Query Syntax

- `is:unread` — Unread messages
- `is:read` — Read messages
- `from:email@example.com` — Messages from specific sender
- `to:email@example.com` — Messages to specific recipient
- `subject:keyword` — Messages with keyword in subject
- `has:attachment` — Messages with attachments
- `before:2026-03-19` — Messages before date
- `after:2026-03-19` — Messages after date

### Label Visibility Options

- `labelShow` — Show label in label list
- `labelHide` — Hide label in label list
- `show` — Show label in message list
- `hide` — Hide label in message list

### Message Output Formats

- `full` — Complete message with headers and body
- `minimal` — Minimal message metadata
- `raw` — Raw RFC 2822 formatted message

### Resource Formats

**Message Resource:**

```
messages/{MESSAGE_ID}
Example: messages/15c2fae3cd77a38f
```

**Thread Resource:**

```
threads/{THREAD_ID}
Example: threads/1489237b8fd3c6e6
```

**Label Resource:**

```
labels/{LABEL_ID}
Example: labels/INBOX, labels/Label_1
```

</details>

---

<details>
<summary><strong>OAuth Guide</strong></summary>

All tools require a valid Google OAuth token. Here's how to obtain one:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API** from the API Library

### Step 2: Create OAuth 2.0 Credentials

1. Navigate to **Credentials** in Google Cloud Console
2. Click **+ Create Credentials** → **OAuth client ID**
3. Select your application type (Desktop, Web, or other)
4. Download the credentials JSON file

### Step 3: Authenticate with Google

Use your Google account to obtain the OAuth token. Refer to [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2) for detailed authentication steps.

### Step 4: Required Scopes

Ensure your OAuth token has these scopes:

- `https://www.googleapis.com/auth/gmail.readonly` — Read-only access to Gmail
- `https://www.googleapis.com/auth/gmail.modify` — Modify Gmail messages and labels
- `https://www.googleapis.com/auth/gmail.send` — Send Gmail messages
- `https://www.googleapis.com/auth/gmail.compose` — Compose Gmail messages as drafts

</details>

---

<details>
<summary><strong>Troubleshooting</strong></summary>

### **Missing or Invalid OAuth Token**

- **Cause:** OAuth token not provided in request or incorrect format
- **Solution:**
  1. Verify `oauth_token` parameter is present in request
  2. Check token is valid and not expired
  3. Obtain a fresh OAuth token from Google

### **Insufficient Permissions**

- **Cause:** OAuth token lacks required scopes for operation
- **Solution:**
  1. Verify token has all required scopes for the operation
  2. Regenerate token with additional scopes if needed
  3. Check Google Cloud project has Gmail API enabled

### **Insufficient Credits**

- **Cause:** API calls have exceeded your requests limits
- **Solution:**
  1. Check credit usage in your Curious Layer dashboard
  2. Upgrade to a paid plan or add credits for higher limits
  3. Contact support for credit adjustments

### **Malformed Request Payload**

- **Cause:** JSON payload is invalid or missing required fields
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure all required parameters are included (`oauth_token`, `message_id`, etc.)
  3. Check parameter types match expected values (string, integer, array)

### **Server Not Found**

- **Cause:** Incorrect server name in the API endpoint
- **Solution:**
  1. Verify endpoint format: `/mcp/{server-name}/{tool-name}`
  2. Use lowercase server name: `/mcp/cl-gmail/...`
  3. Check available servers in documentation

### **Authentication Token Invalid or Expired**

- **Cause:** Token rejected by Gmail API or has expired
- **Solution:**
  1. Obtain a fresh OAuth token from Google
  2. Verify token has all required Gmail scopes
  3. Check token expiration and refresh if needed

</details>

---

<details>
<summary><strong>Resources</strong></summary>

- **[Gmail API Documentation](https://developers.google.com/gmail/api)** — Official API reference
- **[Google Cloud OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)** — Authentication setup guide
- **[Gmail API Reference](https://developers.google.com/gmail/api/reference/rest)** — Complete API endpoint reference
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
</details>

---