# This is the ONLY place where actions are mapped to MCP tools

MCP_ACTION_BINDINGS = {
    "compose_email": {
        "tool": "gmail.reply_thread",
        "args_mapping": {
            "thread_id": "email.thread_id",
            "body": "final_decision.email_body"
        }
    },
    "add_label": {
        "tool": "gmail.add_label",
        "args_mapping": {
            "thread_id": "email.thread_id",
            "label": "final_decision.label"
        }
    },
    "create_calendar_event": {
        "tool": "calendar.create_event",
        "args_mapping": {
            "title": "final_decision.title",
            "start_time": "final_decision.start_time",
            "duration": "final_decision.duration"
        }
    }
}
