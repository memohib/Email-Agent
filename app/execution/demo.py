import json

text = """
UniversalDecisionSchemaV1(schema_version='v1', domain='founder_inbox', intent='draft_reply', category='investor', urgency='same_day', risk_level='low', decision='draft_reply', proposed_actions=[ProposedAction(action_type='compose_email', description='Draft a reply to the email', target='email')], needs_confirmation=True, confidence=0.9, reasoning_summary='The email is a follow-up on a previous discussion and the decision to draft a reply is based on the category_decision_map and the content of the email.')
"""



print(json.loads(text))