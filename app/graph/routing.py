def route_after_confirmation_gate(state):

    """
    Determinsitic router for post-validation / confirmation gate.

    Returns:
    one of "execute", "confirm_interrupt", "fallback"
    """
    validation = state["validation_result"]
    decision = state["decision_output"]
    context  = state["context"]

    if validation.status == "rejected":
        return "fallback"
    
    if decision.needs_confirmation == True:
        human = context.get("human_approval")

        # Not resumed yet → interrupt
        if not human or human.get("approval") is None:
            return "confirm_interrupt"

        # Explicit human rejection
        if human.get("approval") == "rejected":
            return "fallback"

        # Human approval
        if human.get("approval") == "approved":
            return "execute"

        # Defensive default
        return "fallback"

    # -----------------
    # 3. Auto-execute
    # -----------------
    return "execute"
