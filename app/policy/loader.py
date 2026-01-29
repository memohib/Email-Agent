import yaml
from pathlib import Path
from typing import Dict


class PolicyLoader:
    def __init__(self, base_path: str = "policies"):
        self.base_path = Path(base_path)

    def load_domain_policy(self, domain: str) -> Dict[str, dict]:
        domain_path = self.base_path / domain

        if not domain_path.exists():
            raise FileNotFoundError(f"Policy domain not found: {domain}")

        files = {
            "policy": "policy.yaml",
            "categories": "categories.yaml",
            "decisions": "decisions.yaml",
            "actions": "actions.yaml",
            "risk_rules": "risk_rules.yaml"
        }

        loaded = {}
        for key, filename in files.items():
            path = domain_path / filename
            with open(path, "r", encoding="utf-8") as f:
                loaded[key] = yaml.safe_load(f)

        return loaded
