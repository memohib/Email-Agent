from fastmcp import FastMCP
from pydantic import BaseModel
from gmail_client import GmailClient


mcp = FastMCP("gmail-mcp-server")
gmail_client = GmailClient()

class SendEmailArgs(BaseModel):
    to: str
    subject: str
    body: str

class ReplyThreadArgs(BaseModel):
    thread_id: str
    body: str

class ArchiveThreadArgs(BaseModel):
    thread_id: str

class MarkReadArgs(BaseModel):
    thread_id: str

@mcp.tool()
def gmail_send_email(args: SendEmailArgs):
    """
    Send an email via Gmail.
    """
    result = gmail_client.send_email(
        to=args.to,
        subject=args.subject,
        body=args.body
    )
    return {
        "status": "sent",
        "message_id": result["id"]
    }

@mcp.tool()
def gmail_reply_thread(args: ReplyThreadArgs):
    """
    Reply to a thread via Gmail.
    """
    result = gmail_client.reply_thread(
        thread_id=args.thread_id,
        body=args.body
    )
    return {
        "status": "replied",
        "message_id": result["id"]
    }

@mcp.tool()
def gmail_archive_thread(args: ArchiveThreadArgs):
    """
    Archive a thread via Gmail.
    """
    result = gmail_client.archive_thread(
        thread_id=args.thread_id
    )
    return {
        "status": "archived",
        "thread_id": result["id"]
    }

@mcp.tool()
def gmail_mark_read(args: MarkReadArgs):
    """
    Mark a thread as read via Gmail.
    """
    result = gmail_client.mark_read(
        thread_id=args.thread_id
    )
    return {
        "status": "marked as read",
        "thread_id": result["id"]
    }


if __name__ == "__main__":
    mcp.run()