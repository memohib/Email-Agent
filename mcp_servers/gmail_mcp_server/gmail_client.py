import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from auth import get_credentials


class GmailClient:
    def __init__(self):
        creds = get_credentials()
        self.service = build("gmail", "v1", credentials=creds)

    def send_email(self, to: str, subject: str, body: str):
        msg = MIMEText(body)
        msg["to"] = to
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return self.service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

    def reply_thread(self, thread_id: str, body: str):
        msg = MIMEText(body)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        return self.service.users().messages().send(
            userId="me",
            body={"raw": raw, "threadId": thread_id}
        ).execute()

    def archive_thread(self, thread_id: str):
        return self.service.users().threads().modify(
            userId="me",
            id=thread_id,
            body={"removeLabelIds": ["INBOX"]}
        ).execute()

    def mark_read(self, thread_id: str):
        return self.service.users().threads().modify(
            userId="me",
            id=thread_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
