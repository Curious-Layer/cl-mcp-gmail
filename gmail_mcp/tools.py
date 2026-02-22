import base64
import logging
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastmcp import FastMCP

from .schemas import (
    ApiObjectResponse,
    CreateDraftToolResponse,
    CreateLabelToolResponse,
    DraftsListToolResponse,
    IdMessageToolResponse,
    LabelsListToolResponse,
    ModifyLabelsToolResponse,
    OAuthTokenData,
    SearchMessagesToolResponse,
    SendMessageToolResponse,
)
from .service import get_service

logger = logging.getLogger("gmail-mcp-server")


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="get_profile", description="Get the user's Gmail profile information")
    def get_profile(oauth_token: OAuthTokenData) -> ApiObjectResponse:
        """Get authenticated Gmail profile information.

        Args:
            oauth_token: OAuth credentials object with token fields.

        Returns:
            Gmail profile object (e.g., email address, message/thread totals) or error.
        """
        logger.info("Executing get_profile")
        try:
            service = get_service(oauth_token)
            profile = service.users().getProfile(userId="me").execute()
            logger.info(f"Retrieved profile for: {profile.get('emailAddress')}")
            return profile
        except Exception as e:
            logger.error(f"Error in get_profile: {e}")
            return {"error": str(e)}

    @mcp.tool(
        name="get_message", description="Get a specific message by ID with full details"
    )
    def get_message(
        oauth_token: OAuthTokenData, message_id: str, format: str = "full"
    ) -> ApiObjectResponse:
        """Get a message by Gmail message ID.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Gmail message ID.
            format: Gmail message format. Common values: `minimal`, `full`, `raw`,
                `metadata`.

        Returns:
            Gmail message object in requested format or error.
        """
        logger.info(f"Executing get_message for ID: {message_id}")
        try:
            service = get_service(oauth_token)
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
        oauth_token: OAuthTokenData,
        to: str,
        subject: str,
        body: str,
        cc: str = "",
        bcc: str = "",
    ) -> SendMessageToolResponse:
        """Send a plain-text email.

        Args:
            oauth_token: OAuth credentials object with token fields.
            to: Recipient email address.
            subject: Email subject.
            body: Plain-text email body.
            cc: Optional comma-separated CC recipients.
            bcc: Optional comma-separated BCC recipients.

        Returns:
            Delivery status with sent message ID/thread ID or error.
        """
        logger.info(f"Executing send_message to: {to}")
        try:
            service = get_service(oauth_token)

            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_message_result = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            logger.info(f"Message sent successfully: {send_message_result.get('id')}")
            return {
                "message": "Email sent successfully",
                "id": send_message_result.get("id", ""),
                "threadId": send_message_result.get("threadId", ""),
            }
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            return {"error": str(e)}

    @mcp.tool(
        name="send_message_with_attachment",
        description="Send an email message with file attachments",
    )
    def send_message_with_attachment(
        oauth_token: OAuthTokenData,
        to: str,
        subject: str,
        body: str,
        attachment_path: str,
        cc: str = "",
    ) -> SendMessageToolResponse:
        """Send an email with one attachment file.

        Args:
            oauth_token: OAuth credentials object with token fields.
            to: Recipient email address.
            subject: Email subject.
            body: Plain-text email body.
            attachment_path: Local path to file attachment.
            cc: Optional comma-separated CC recipients.

        Returns:
            Delivery status with sent message ID/thread ID or error.
        """
        logger.info(f"Executing send_message_with_attachment to: {to}")
        try:
            service = get_service(oauth_token)

            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = cc

            message.attach(MIMEText(body, "plain"))

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

            send_message_result = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            logger.info(
                "Message with attachment sent successfully: "
                f"{send_message_result.get('id')}"
            )
            return {
                "message": "Email with attachment sent successfully",
                "id": send_message_result.get("id", ""),
                "threadId": send_message_result.get("threadId", ""),
            }
        except Exception as e:
            logger.error(f"Error in send_message_with_attachment: {e}")
            return {"error": str(e)}

    @mcp.tool(name="reply_to_message", description="Reply to an existing email message")
    def reply_to_message(
        oauth_token: OAuthTokenData, message_id: str, body: str
    ) -> SendMessageToolResponse:
        """Reply to an existing Gmail message.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Original Gmail message ID to reply to.
            body: Reply body text.

        Returns:
            Delivery status with reply message ID/thread ID or error.
        """
        logger.info(f"Executing reply_to_message for ID: {message_id}")
        try:
            service = get_service(oauth_token)

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

            message = MIMEText(body)
            message["to"] = headers.get("From", "")
            message["subject"] = "Re: " + headers.get("Subject", "").replace("Re: ", "")
            message["In-Reply-To"] = headers.get("Message-ID", "")
            message["References"] = headers.get("Message-ID", "")

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_message_result = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message, "threadId": thread_id})
                .execute()
            )

            logger.info(f"Reply sent successfully: {send_message_result.get('id')}")
            return {
                "message": "Reply sent successfully",
                "id": send_message_result.get("id", ""),
                "threadId": send_message_result.get("threadId", ""),
            }
        except Exception as e:
            logger.error(f"Error in reply_to_message: {e}")
            return {"error": str(e)}

    @mcp.tool(name="delete_message", description="Delete a message permanently")
    def delete_message(
        oauth_token: OAuthTokenData, message_id: str
    ) -> IdMessageToolResponse:
        """Permanently delete a Gmail message.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Gmail message ID.

        Returns:
            Deletion status with target message ID or error.
        """
        logger.info(f"Executing delete_message for ID: {message_id}")
        try:
            service = get_service(oauth_token)
            service.users().messages().delete(userId="me", id=message_id).execute()
            logger.info("Message deleted successfully")
            return {"message": f"Message {message_id} deleted successfully", "id": message_id}
        except Exception as e:
            logger.error(f"Error in delete_message: {e}")
            return {"error": str(e)}

    @mcp.tool(name="trash_message", description="Move a message to trash")
    def trash_message(
        oauth_token: OAuthTokenData, message_id: str
    ) -> IdMessageToolResponse:
        """Move a Gmail message to trash.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Gmail message ID.

        Returns:
            Trash operation status and affected message ID or error.
        """
        logger.info(f"Executing trash_message for ID: {message_id}")
        try:
            service = get_service(oauth_token)
            message = service.users().messages().trash(userId="me", id=message_id).execute()
            logger.info("Message moved to trash")
            return {
                "message": "Message moved to trash successfully",
                "id": message.get("id", ""),
            }
        except Exception as e:
            logger.error(f"Error in trash_message: {e}")
            return {"error": str(e)}

    @mcp.tool(name="untrash_message", description="Remove a message from trash")
    def untrash_message(
        oauth_token: OAuthTokenData, message_id: str
    ) -> IdMessageToolResponse:
        """Restore a trashed Gmail message.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Gmail message ID.

        Returns:
            Restore operation status and affected message ID or error.
        """
        logger.info(f"Executing untrash_message for ID: {message_id}")
        try:
            service = get_service(oauth_token)
            message = service.users().messages().untrash(userId="me", id=message_id).execute()
            logger.info("Message removed from trash")
            return {
                "message": "Message removed from trash successfully",
                "id": message.get("id", ""),
            }
        except Exception as e:
            logger.error(f"Error in untrash_message: {e}")
            return {"error": str(e)}

    @mcp.tool(name="modify_message_labels", description="Add or remove labels from a message")
    def modify_message_labels(
        oauth_token: OAuthTokenData,
        message_id: str,
        add_labels: list[str] = [],
        remove_labels: list[str] = [],
    ) -> ModifyLabelsToolResponse:
        """Add and/or remove labels from a message.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Gmail message ID.
            add_labels: Label IDs to add.
            remove_labels: Label IDs to remove.

        Returns:
            Label modification status, message ID, current labels, or error.
        """
        logger.info(f"Executing modify_message_labels for ID: {message_id}")
        try:
            service = get_service(oauth_token)

            body = {}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            message = (
                service.users().messages().modify(userId="me", id=message_id, body=body).execute()
            )

            logger.info("Message labels modified successfully")
            return {
                "message": "Labels modified successfully",
                "id": message.get("id", ""),
                "labelIds": message.get("labelIds", []),
            }
        except Exception as e:
            logger.error(f"Error in modify_message_labels: {e}")
            return {"error": str(e)}

    @mcp.tool(name="list_labels", description="Get all labels in the user's mailbox")
    def list_labels(oauth_token: OAuthTokenData) -> LabelsListToolResponse:
        """List all labels in the mailbox.

        Args:
            oauth_token: OAuth credentials object with token fields.

        Returns:
            Label count and label objects or error.
        """
        logger.info("Executing list_labels")
        try:
            service = get_service(oauth_token)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            logger.info(f"Found {len(labels)} labels")
            return {"count": len(labels), "labels": labels}
        except Exception as e:
            logger.error(f"Error in list_labels: {e}")
            return {"error": str(e)}

    @mcp.tool(name="create_label", description="Create a new label")
    def create_label(
        oauth_token: OAuthTokenData,
        name: str,
        label_list_visibility: str = "labelShow",
        message_list_visibility: str = "show",
    ) -> CreateLabelToolResponse:
        """Create a Gmail label.

        Args:
            oauth_token: OAuth credentials object with token fields.
            name: Display name of the label.
            label_list_visibility: Label list visibility. Common values include
                `labelShow`, `labelShowIfUnread`, `labelHide`.
            message_list_visibility: Message list visibility. Common values include
                `show`, `hide`.

        Returns:
            Creation status and created label object or error.
        """
        logger.info(f"Executing create_label: {name}")
        try:
            service = get_service(oauth_token)

            label = {
                "name": name,
                "labelListVisibility": label_list_visibility,
                "messageListVisibility": message_list_visibility,
            }

            created_label = service.users().labels().create(userId="me", body=label).execute()

            logger.info(f"Label created successfully: {created_label.get('id')}")
            return {"message": "Label created successfully", "label": created_label}
        except Exception as e:
            logger.error(f"Error in create_label: {e}")
            return {"error": str(e)}

    @mcp.tool(name="delete_label", description="Delete a label")
    def delete_label(oauth_token: OAuthTokenData, label_id: str) -> IdMessageToolResponse:
        """Delete a Gmail label.

        Args:
            oauth_token: OAuth credentials object with token fields.
            label_id: Gmail label ID.

        Returns:
            Deletion status with label ID or error.
        """
        logger.info(f"Executing delete_label for ID: {label_id}")
        try:
            service = get_service(oauth_token)
            service.users().labels().delete(userId="me", id=label_id).execute()
            logger.info("Label deleted successfully")
            return {"message": f"Label {label_id} deleted successfully", "id": label_id}
        except Exception as e:
            logger.error(f"Error in delete_label: {e}")
            return {"error": str(e)}

    @mcp.tool(name="search_messages", description="Search messages using Gmail search syntax")
    def search_messages(
        oauth_token: OAuthTokenData, query: str, max_results: int = 10
    ) -> SearchMessagesToolResponse:
        """Search messages using Gmail query syntax.

        Args:
            oauth_token: OAuth credentials object with token fields.
            query: Gmail search query (e.g., `from:example@x.com is:unread`).
            max_results: Maximum messages to return (server caps at 500).

        Returns:
            Match count, message stubs, estimate, or error.
        """
        logger.info(f"Executing search_messages with query: {query}")
        try:
            service = get_service(oauth_token)

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
    def mark_as_read(
        oauth_token: OAuthTokenData, message_id: str
    ) -> IdMessageToolResponse:
        """Mark a message as read by removing `UNREAD` label.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Gmail message ID.

        Returns:
            Operation status and message ID or error.
        """
        logger.info(f"Executing mark_as_read for ID: {message_id}")
        try:
            service = get_service(oauth_token)

            message = (
                service.users()
                .messages()
                .modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]})
                .execute()
            )

            logger.info("Message marked as read")
            return {
                "message": "Message marked as read successfully",
                "id": message.get("id", ""),
            }
        except Exception as e:
            logger.error(f"Error in mark_as_read: {e}")
            return {"error": str(e)}

    @mcp.tool(name="mark_as_unread", description="Mark a message as unread")
    def mark_as_unread(
        oauth_token: OAuthTokenData, message_id: str
    ) -> IdMessageToolResponse:
        """Mark a message as unread by adding `UNREAD` label.

        Args:
            oauth_token: OAuth credentials object with token fields.
            message_id: Gmail message ID.

        Returns:
            Operation status and message ID or error.
        """
        logger.info(f"Executing mark_as_unread for ID: {message_id}")
        try:
            service = get_service(oauth_token)

            message = (
                service.users()
                .messages()
                .modify(userId="me", id=message_id, body={"addLabelIds": ["UNREAD"]})
                .execute()
            )

            logger.info("Message marked as unread")
            return {
                "message": "Message marked as unread successfully",
                "id": message.get("id", ""),
            }
        except Exception as e:
            logger.error(f"Error in mark_as_unread: {e}")
            return {"error": str(e)}

    @mcp.tool(name="get_thread", description="Get an entire email thread")
    def get_thread(
        oauth_token: OAuthTokenData, thread_id: str, format: str = "full"
    ) -> ApiObjectResponse:
        """Retrieve a full Gmail thread.

        Args:
            oauth_token: OAuth credentials object with token fields.
            thread_id: Gmail thread ID.
            format: Thread message format. Common values: `minimal`, `full`, `raw`,
                `metadata`.

        Returns:
            Thread object with messages or error.
        """
        logger.info(f"Executing get_thread for ID: {thread_id}")
        try:
            service = get_service(oauth_token)

            thread = (
                service.users().threads().get(userId="me", id=thread_id, format=format).execute()
            )

            logger.info(f"Retrieved thread with {len(thread.get('messages', []))} messages")
            return thread
        except Exception as e:
            logger.error(f"Error in get_thread: {e}")
            return {"error": str(e)}

    @mcp.tool(name="list_drafts", description="List draft messages")
    def list_drafts(
        oauth_token: OAuthTokenData, max_results: int = 10
    ) -> DraftsListToolResponse:
        """List draft messages.

        Args:
            oauth_token: OAuth credentials object with token fields.
            max_results: Maximum drafts to return (server caps at 500).

        Returns:
            Draft count and draft stubs or error.
        """
        logger.info("Executing list_drafts")
        try:
            service = get_service(oauth_token)

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
    def create_draft(
        oauth_token: OAuthTokenData, to: str, subject: str, body: str
    ) -> CreateDraftToolResponse:
        """Create a new draft email.

        Args:
            oauth_token: OAuth credentials object with token fields.
            to: Recipient email address.
            subject: Draft subject.
            body: Draft body text.

        Returns:
            Draft creation status and draft ID or error.
        """
        logger.info(f"Executing create_draft to: {to}")
        try:
            service = get_service(oauth_token)

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
            return {"message": "Draft created successfully", "id": draft.get("id", "")}
        except Exception as e:
            logger.error(f"Error in create_draft: {e}")
            return {"error": str(e)}
