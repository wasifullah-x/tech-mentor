"""
Tests for Safety Checker
"""
import pytest
from services.safety_checker import SafetyChecker


@pytest.fixture
def safety_checker():
    return SafetyChecker()


def test_check_safe_solutions(safety_checker):
    """Test checking safe solutions"""
    steps = [
        {
            "step_number": 1,
            "action": "Restart your computer",
            "risk_level": "safe"
        },
        {
            "step_number": 2,
            "action": "Check network settings",
            "risk_level": "safe"
        }
    ]
    
    warnings = safety_checker.check_solutions(steps)
    assert len(warnings) == 0


def test_check_risky_solutions(safety_checker):
    """Test checking risky solutions"""
    steps = [
        {
            "step_number": 1,
            "action": "Format the hard drive",
            "risk_level": "risky"
        }
    ]
    
    warnings = safety_checker.check_solutions(steps)
    assert len(warnings) > 0
    assert any("backup" in w.lower() or "erase" in w.lower() for w in warnings)


def test_requires_professional_help(safety_checker):
    """Test professional help detection"""
    # Physical danger
    assert safety_checker.requires_professional_help(
        "My laptop is smoking",
        []
    ) is True
    
    # Hardware repair
    assert safety_checker.requires_professional_help(
        "Need to replace motherboard",
        []
    ) is True
    
    # Simple issue
    assert safety_checker.requires_professional_help(
        "Forgot my password",
        [{"step_number": 1, "action": "Reset password"}]
    ) is False


def test_check_command_safety(safety_checker):
    """Test command safety checking"""
    # Safe command
    result = safety_checker.check_command_safety("ipconfig")
    assert result["is_safe"] is True
    assert result["risk_level"] == "safe"
    
    # Dangerous command
    result = safety_checker.check_command_safety("rm -rf /")
    assert result["is_safe"] is False
    assert result["risk_level"] == "dangerous"
    
    # Risky command
    result = safety_checker.check_command_safety("reg delete HKLM")
    assert result["risk_level"] == "risky"
    assert len(result["warnings"]) > 0
