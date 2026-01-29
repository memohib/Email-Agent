from .models import CompiledPolicy, AutonomyPolicy
from .exceptions import PolicyValidationError
from .mcp_bindings import MCP_ACTION_BINDINGS


class PolicyCompiler:

    def compile(self, raw: dict) -> CompiledPolicy:
        policy = raw["policy"]
        autonomy = policy.get("autonomy")  # Get autonomy from policy, not from raw
        categories = raw["categories"]["categories"]
        decisions = raw["decisions"]["decisions"]
        actions = self._bind_mcp_tools(raw["actions"]["actions"])
        risk_rules = raw["risk_rules"]


        autonomy_level = autonomy.get("level", "manual_only") if autonomy else "manual_only"
        
        self._validate_references(categories, decisions, actions)

        return CompiledPolicy(
            domain=policy["domain"],
            version=policy["version"],
            autonomy=AutonomyPolicy(level=autonomy_level),
            categories=categories,
            decisions=decisions,
            actions=actions,

            risk_levels=risk_rules["risk_levels"],
            urgency_levels=risk_rules["urgency_levels"],
            risk_urgency_matrix=risk_rules["risk_urgency_matrix"],
            risk_constraints=risk_rules["risk_constraints"],

            global_rules=policy["global_rules"],
            default_fallback_decision=policy["default_fallback_decision"]
        )

    def _validate_references(self, categories, decisions, actions):
        # Category → Decision integrity
        for category, cfg in categories.items():
            for decision in cfg["allowed_decisions"]:
                if decision not in decisions:
                    raise PolicyValidationError(
                        f"Category '{category}' references unknown decision '{decision}'"
                    )

        # Decision → Action integrity
        for decision, cfg in decisions.items():
            for action in cfg["allowed_actions"]:
                if action not in actions:
                    raise PolicyValidationError(
                        f"Decision '{decision}' references unknown action '{action}'"
                    )

    def _bind_mcp_tools(self, actions: dict) -> dict:
        compiled = {}

        for action_name, action_def in actions.items():
            action = dict(action_def)  # shallow copy

            if action.get("external") is True:
                if action_name not in MCP_ACTION_BINDINGS:
                    raise RuntimeError(
                        f"External action '{action_name}' has no MCP binding"
                    )

                action["mcp"] = MCP_ACTION_BINDINGS[action_name]

            compiled[action_name] = action

        return compiled

