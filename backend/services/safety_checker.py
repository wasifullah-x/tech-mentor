"""
Safety Checker - Validates solutions for safety and provides warnings
"""
from typing import List, Dict, Any
import re
from loguru import logger


class SafetyChecker:
    """
    Checks solutions for safety concerns and generates warnings
    """
    
    # Risky keywords that require warnings
    RISKY_KEYWORDS = {
        "format": "⚠️ WARNING: This will erase all data. BACKUP FIRST!",
        "delete": "⚠️ CAUTION: Deleting system files can cause problems. Double-check before proceeding.",
        "registry": "⚠️ WARNING: Editing the registry can damage Windows. Create a restore point first.",
        "reset": "⚠️ WARNING: Factory reset will erase all data. BACKUP FIRST!",
        "reinstall": "⚠️ CAUTION: Reinstalling may lose data. Backup important files first.",
        "bios": "⚠️ WARNING: Incorrect BIOS settings can prevent boot. Only proceed if confident.",
        "firmware": "⚠️ CAUTION: Failed firmware updates can brick devices. Ensure stable power.",
        "partition": "⚠️ WARNING: Partitioning errors can cause data loss. BACKUP FIRST!",
    }
    
    # Physical safety concerns
    PHYSICAL_DANGER_KEYWORDS = [
        "smoking", "burning", "smell", "sparks", "hot", "shock", 
        "electric", "fire", "melting"
    ]
    
    # Hardware repair indicators
    HARDWARE_KEYWORDS = [
        "open case", "remove screws", "thermal paste", "replace component",
        "disassemble", "solder", "hardware repair"
    ]
    
    def check_solutions(self, solution_steps: List[Dict[str, Any]]) -> List[str]:
        """
        Check solution steps for safety concerns
        
        Args:
            solution_steps: List of solution step dictionaries
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        for step in solution_steps:
            action = step.get("action", "").lower()
            
            # Check for risky keywords
            for keyword, warning in self.RISKY_KEYWORDS.items():
                if keyword in action:
                    if warning not in warnings:
                        warnings.append(warning)
            
            # Check risk level
            if step.get("risk_level") == "risky":
                warnings.append(
                    f"⚠️ Step {step.get('step_number')}: This action carries some risk. "
                    "Proceed carefully and ensure you understand what it does."
                )
        
        return warnings
    
    def requires_professional_help(
        self,
        problem_description: str,
        solution_steps: List[Dict[str, Any]]
    ) -> bool:
        """
        Determine if the problem requires professional assistance
        
        Args:
            problem_description: Description of the problem
            solution_steps: Proposed solution steps
        
        Returns:
            True if professional help is recommended
        """
        problem_lower = problem_description.lower()
        
        # Physical danger - immediate professional help
        if any(keyword in problem_lower for keyword in self.PHYSICAL_DANGER_KEYWORDS):
            logger.warning(f"Physical danger detected in problem: {problem_description[:100]}")
            return True
        
        # Hardware repair requirements
        if any(keyword in problem_lower for keyword in self.HARDWARE_KEYWORDS):
            return True
        
        # Complex hardware issues
        complex_hardware = [
            "won't turn on", "no power", "physical damage", "dropped",
            "water damage", "screen broken", "motherboard"
        ]
        if any(phrase in problem_lower for phrase in complex_hardware):
            # Check if simple solutions exist
            if len(solution_steps) < 3:
                return True
        
        return False
    
    def check_command_safety(self, command: str) -> Dict[str, Any]:
        """
        Check if a specific command or action is safe
        
        Args:
            command: Command or action to check
        
        Returns:
            Dictionary with safety assessment
        """
        command_lower = command.lower()
        
        result = {
            "is_safe": True,
            "risk_level": "safe",
            "warnings": [],
            "requires_confirmation": False
        }
        
        # Check for extremely dangerous commands
        dangerous_patterns = [
            r"rm\s+-rf\s+/",  # Unix delete everything
            r"del\s+/f\s+/s\s+/q\s+[A-Z]:\\",  # Windows delete everything
            r"format\s+[A-Z]:",  # Format drive
            r"dd\s+if=/dev/zero",  # Overwrite disk
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                result["is_safe"] = False
                result["risk_level"] = "dangerous"
                result["warnings"].append("🛑 DANGEROUS: This command can cause permanent data loss!")
                result["requires_confirmation"] = True
                return result
        
        # Check for risky operations
        risky_patterns = [
            (r"reg\s+(add|delete)", "registry", "Modifying Windows registry"),
            (r"chmod\s+777", "permissions", "Opening full permissions is insecure"),
            (r"sudo\s+rm", "deletion", "Deleting system files with elevated privileges"),
        ]
        
        for pattern, category, description in risky_patterns:
            if re.search(pattern, command_lower):
                result["risk_level"] = "risky"
                result["warnings"].append(f"⚠️ RISKY: {description}")
                result["requires_confirmation"] = True
        
        # Check for administrative privileges
        if any(word in command_lower for word in ["sudo", "admin", "elevated"]):
            result["warnings"].append("ℹ️ This requires administrative privileges")
        
        return result
    
    def generate_safety_briefing(
        self,
        problem_description: str,
        solution_steps: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a safety briefing for the user
        
        Args:
            problem_description: The problem being solved
            solution_steps: The proposed solutions
        
        Returns:
            Safety briefing text
        """
        briefing = []
        
        # Check for data loss risk
        if any(keyword in problem_description.lower() 
               for keyword in ["reset", "format", "reinstall"]):
            briefing.append(
                "📋 BACKUP REMINDER: This solution may involve data loss. "
                "Please backup important files before proceeding."
            )
        
        # Check for professional help
        if self.requires_professional_help(problem_description, solution_steps):
            briefing.append(
                "👨‍🔧 PROFESSIONAL HELP: This issue may require professional assistance. "
                "If you're not comfortable with these steps, consider consulting a technician."
            )
        
        # Check for physical danger
        if any(keyword in problem_description.lower() 
               for keyword in self.PHYSICAL_DANGER_KEYWORDS):
            briefing.append(
                "🛑 SAFETY WARNING: Disconnect power immediately and do not attempt repair. "
                "Contact a professional technician or the manufacturer."
            )
        
        # General safety reminder
        if any(step.get("risk_level") in ["caution", "risky"] for step in solution_steps):
            briefing.append(
                "⚡ CAUTION: Some steps require care. Read each instruction completely "
                "before performing it."
            )
        
        return "\n\n".join(briefing) if briefing else ""
    
    def validate_user_action(self, action_description: str) -> Dict[str, Any]:
        """
        Validate an action the user wants to take
        
        Args:
            action_description: What the user wants to do
        
        Returns:
            Validation result with recommendations
        """
        action_lower = action_description.lower()
        
        result = {
            "approved": True,
            "warnings": [],
            "recommendations": [],
            "alternative": None
        }
        
        # Check for dangerous actions
        if "open" in action_lower and any(word in action_lower for word in ["laptop", "computer", "case"]):
            result["warnings"].append(
                "Opening your device may void warranty and risks static damage to components."
            )
            result["recommendations"].append(
                "Ground yourself with an anti-static wrist strap before touching internal components."
            )
        
        # Check for software installations from unknown sources
        if "download" in action_lower or "install" in action_lower:
            result["recommendations"].append(
                "Only download software from official sources to avoid malware."
            )
        
        # Check for BIOS modifications
        if "bios" in action_lower or "uefi" in action_lower:
            result["warnings"].append(
                "Incorrect BIOS settings can prevent your computer from booting."
            )
            result["recommendations"].append(
                "Write down current settings before making changes so you can revert if needed."
            )
        
        return result
