import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.policy.compiler import PolicyCompiler

def test_binding():
    print("Testing PolicyCompiler binding...")
    
    compiler = PolicyCompiler()
    
    # Test case 1: Valid external action
    raw_valid = {
        "policy": {
            "domain": "test",
            "version": "1.0",
            "autonomy": {"level": "manual_only"},
            "global_rules": {},
            "default_fallback_decision": "none"
        },
        "categories": {"categories": {}},
        "decisions": {"decisions": {}},
        "actions": {"actions": {
            "compose_email": {"external": True, "description": "Compose an email"},
            "internal_op": {"external": False, "description": "Internal operation"}
        }},
        "risk_rules": {
            "risk_levels": [],
            "urgency_levels": [],
            "risk_urgency_matrix": {},
            "risk_constraints": {}
        }
    }
    
    try:
        compiled = compiler.compile(raw_valid)
        print("✅ Compilation successful for valid actions.")
        
        # Check if 'mcp' key is added to compose_email
        action = compiled.actions["compose_email"]
        if "mcp" in action:
            print(f"✅ 'mcp' binding found for 'compose_email': {action['mcp']['tool']}")
        else:
            print("❌ 'mcp' binding MISSING for 'compose_email'")
            
        # Check internal op has no mcp
        if "mcp" not in compiled.actions["internal_op"]:
             print("✅ Internal action correct (no mcp).")

    except Exception as e:
        print(f"❌ Compilation failed unexpectedly: {e}")
        import traceback
        traceback.print_exc()

    # Test case 2: Invalid external action
    raw_invalid = {
        "policy": raw_valid["policy"],
        "categories": raw_valid["categories"],
        "decisions": raw_valid["decisions"],
        "actions": {"actions": {
            "unknown_action": {"external": True}
        }},
        "risk_rules": raw_valid["risk_rules"]
    }
    
    print("\nTesting missing binding detection...")
    try:
        compiler.compile(raw_invalid)
        print("❌ Failed to detect missing binding for 'unknown_action'")
    except RuntimeError as e:
        print(f"✅ Correctly caught error: {e}")
    except Exception as e:
        print(f"❌ Caught wrong exception type: {type(e)}")

if __name__ == "__main__":
    test_binding()
