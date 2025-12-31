"""
Reasoning Engine - Multi-step problem diagnosis and solution generation
"""
from typing import List, Dict, Optional, Any
import json
import re
from loguru import logger

from services.rag_service import RAGService
from services.llm_service import LLMService
from services.safety_checker import SafetyChecker
from services.question_catalog import FOLLOW_UP_QUESTIONS
from api.models import DeviceInfo, Cause, SolutionStep


class ReasoningEngine:
    """
    Implements multi-step reasoning for IT problem diagnosis
    """
    
    def __init__(self, rag_service: RAGService, llm_service: LLMService):
        self.rag_service = rag_service
        self.llm_service = llm_service
        self.safety_checker = SafetyChecker()
    
    async def diagnose_and_solve(
        self,
        user_problem: str,
        conversation_history: List[Dict],
        device_info: Optional[DeviceInfo] = None,
        technical_level: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Main reasoning loop: understand → retrieve → analyze → solve
        
        Args:
            user_problem: User's problem description
            conversation_history: Previous conversation
            device_info: Device information
            technical_level: User's technical expertise
        
        Returns:
            Complete response with diagnosis and solutions
        """
        logger.info(f"Processing problem: {user_problem[:100]}...")

        # Handle greetings / small-talk without forcing a troubleshooting prompt.
        if self._is_greeting_or_smalltalk(user_problem):
            greeting_text = (
                "Hi! I can help troubleshoot tech issues.\n\n"
                "Tell me what’s going wrong and I’ll walk you through it. If you can, include:\n"
                "- Your device type (laptop/desktop/phone/printer, etc.)\n"
                "- Your OS (Windows/macOS/Android/iOS/Linux)\n"
                "- Any exact error message\n\n"
                "Example: ‘My Windows laptop can’t connect to Wi‑Fi after an update.’"
            )
            return {
                "response": greeting_text,
                "reasoning_type": "onboarding",
                "problem_understanding": "Greeting / onboarding",
                "likely_causes": [],
                "solution_steps": [],
                "next_steps": "Describe the issue you want to fix (what you expected vs what happened).",
                "follow_up_question": FOLLOW_UP_QUESTIONS["onboarding"],
                "warnings": [],
                "requires_professional_help": False,
                "sources": [],
            }
        
        # Step 1: Rephrase and understand the problem
        rephrased_problem = await self._rephrase_query(user_problem, device_info)
        logger.info(f"Rephrased: {rephrased_problem}")
        
        # Step 2: Check if helpful information is missing.
        # IMPORTANT: Do not block the response. We still provide best-effort help,
        # and ask one targeted follow-up question.
        follow_up_question = self._check_missing_info(user_problem, device_info)
        
        # Step 3: Retrieve relevant knowledge
        knowledge_results = await self.rag_service.retrieve_solutions(
            query=rephrased_problem,
            top_k=5
        )

        reasoning_type = self._determine_reasoning_type(
            knowledge_results=knowledge_results,
            follow_up_question=follow_up_question,
        )
        
        # Format knowledge context
        knowledge_context = self._format_knowledge_context(knowledge_results)
        logger.info(f"Retrieved {len(knowledge_results)} relevant solutions")
        
        # Step 4: Analyze causes
        likely_causes = await self._analyze_causes(
            rephrased_problem,
            knowledge_results,
            device_info
        )
        
        # Step 5: Generate solution steps
        solution_steps = await self._generate_solution_steps(
            rephrased_problem,
            likely_causes,
            knowledge_results,
            conversation_history
        )
        
        # Step 6: Safety check
        warnings = self.safety_checker.check_solutions(solution_steps)
        requires_professional = self.safety_checker.requires_professional_help(
            rephrased_problem,
            solution_steps
        )
        
        # Step 7: Generate natural language response
        system_prompt = self.llm_service.format_system_prompt(
            knowledge_context=knowledge_context,
            device_info=device_info.dict() if device_info else None,
            technical_level=technical_level
        )
        
        # Build user message with context
        user_message = f"""User's problem: {user_problem}

Based on my analysis:
- Problem type: {rephrased_problem}
- Likely causes: {', '.join([c['cause'] for c in likely_causes[:3]])}

"""

        if follow_up_question:
            user_message += f"\nMissing info to ask at the end (one question): {follow_up_question}\n"

        user_message += "\nGenerate a helpful, friendly response following the mandatory structure. Include specific step-by-step instructions."

        response_text = await self.llm_service.generate_completion(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=conversation_history[-6:] if conversation_history else None
        )

        # If the LLM layer is in fallback or returned something unhelpful,
        # generate a clean structured response from our inference outputs.
        if not response_text or "technical difficulties" in response_text.lower():
            response_text = self._build_structured_response(
                problem_understanding=rephrased_problem,
                likely_causes=likely_causes,
                solution_steps=solution_steps,
                next_steps=None,
                follow_up_question=follow_up_question,
            )
        
        # Step 8: Determine next steps
        next_steps = self._generate_next_steps(solution_steps, requires_professional)

        # Ensure response includes coherent next steps even in fallback mode.
        if not response_text or "next steps" not in response_text.lower():
            response_text = self._build_structured_response(
                problem_understanding=rephrased_problem,
                likely_causes=likely_causes,
                solution_steps=solution_steps,
                next_steps=next_steps,
                follow_up_question=follow_up_question,
            )

        # Ensure the user sees the follow-up question in the chat text even if
        # the frontend doesn't render follow_up_question separately.
        if follow_up_question and follow_up_question.lower() not in response_text.lower():
            response_text = response_text.rstrip() + f"\n\n**Quick question:** {follow_up_question}"
        
        # Extract sources
        sources = [result.get("problem", "") for result in knowledge_results[:3]]
        
        return {
            "response": response_text,
            "reasoning_type": reasoning_type,
            "problem_understanding": rephrased_problem,
            "likely_causes": likely_causes,
            "solution_steps": solution_steps,
            "next_steps": next_steps,
            "follow_up_question": follow_up_question,
            "warnings": warnings,
            "requires_professional_help": requires_professional,
            "sources": sources
        }

    def _determine_reasoning_type(
        self,
        knowledge_results: List[Dict],
        follow_up_question: Optional[str],
    ) -> str:
        """Return a stable label describing which reasoning route was used.

        This is intentionally high-level and deterministic so it can be displayed
        to users and asserted in tests without requiring access to hidden
        chain-of-thought.
        """
        retrieval = "rag" if knowledge_results else "no_kb_match"
        llm = (
            "remote_llm"
            if (getattr(self.llm_service, "openai_client", None) or getattr(self.llm_service, "anthropic_client", None))
            else "deterministic_fallback"
        )
        clarifying = "asked_follow_up" if follow_up_question else "no_follow_up"
        return f"{retrieval}+{llm}+{clarifying}"

    def _is_greeting_or_smalltalk(self, text: str) -> bool:
        cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower()).strip()
        if not cleaned:
            return False

        # If it already contains troubleshooting intent, treat it as a problem.
        troubleshooting_terms = {
            "wifi", "wi fi", "internet", "network", "slow", "lag", "freeze", "frozen",
            "crash", "bsod", "blue", "screen", "printer", "battery", "update", "error",
            "won't", "wont", "can't", "cant", "not", "broken", "stuck", "virus", "malware",
        }
        if any(term in cleaned for term in troubleshooting_terms):
            return False

        # Pure greetings / small-talk should get a friendly response.
        greetings = {
            "hi", "hello", "hey", "hiya", "yo", "howdy", "sup",
            "good morning", "good afternoon", "good evening",
            "how are you", "whats up", "what's up", "help",
        }

        if cleaned in greetings:
            return True

        tokens = cleaned.split()
        if len(tokens) <= 3 and tokens[0] in {"hi", "hello", "hey", "hiya", "yo", "howdy", "sup"}:
            return True

        # Short messages that are not technical but not necessarily in the list.
        if len(tokens) <= 3 and all(t.isalpha() for t in tokens):
            return True

        return False

    def _build_structured_response(
        self,
        problem_understanding: str,
        likely_causes: List[Dict[str, Any]],
        solution_steps: List[Dict[str, Any]],
        next_steps: Optional[str],
        follow_up_question: Optional[str],
    ) -> str:
        # Keep formatting stable for the frontend.
        lines: List[str] = []

        lines.append("1. **Problem Understanding**")
        lines.append(problem_understanding.strip() if problem_understanding else "(unknown)")
        lines.append("")

        lines.append("2. **Likely Causes**")
        if likely_causes:
            for cause in likely_causes[:4]:
                cause_text = str(cause.get("cause", "")).strip()
                likelihood = str(cause.get("likelihood", "")).strip()
                explanation = str(cause.get("explanation", "")).strip()
                bullet = f"- {cause_text}"
                if likelihood:
                    bullet += f" ({likelihood})"
                if explanation:
                    bullet += f": {explanation}"
                lines.append(bullet)
        else:
            lines.append("- (No specific causes found — using general troubleshooting)")
        lines.append("")

        lines.append("3. **Step-by-Step Solution**")
        if solution_steps:
            # Sort steps defensively
            sorted_steps = sorted(solution_steps, key=lambda s: int(s.get("step_number", 9999)))
            for step in sorted_steps[:10]:
                n = step.get("step_number", "")
                action = str(step.get("action", "")).strip()
                explanation = str(step.get("explanation", "")).strip()
                if not action:
                    continue
                if n:
                    lines.append(f"{n}. {action}")
                else:
                    lines.append(f"- {action}")
                if explanation:
                    lines.append(f"   - Why: {explanation}")
        else:
            lines.append("1. Restart the device")
            lines.append("   - Why: Clears temporary glitches")
        lines.append("")

        lines.append("4. **Next Steps**")
        lines.append(next_steps.strip() if next_steps else "If this didn’t work, tell me what happened at each step and any exact error message you see.")
        lines.append("")

        lines.append("5. **Follow-up Question**")
        lines.append(follow_up_question.strip() if follow_up_question else "(None)")

        return "\n".join(lines)
    
    async def analyze_problem(
        self,
        problem_description: str,
        device_info: Optional[DeviceInfo] = None
    ) -> Dict[str, Any]:
        """
        Analyze a problem without providing full solution
        """
        # Retrieve knowledge
        knowledge_results = await self.rag_service.retrieve_solutions(
            query=problem_description,
            top_k=3
        )
        
        # Determine category
        category = self._categorize_problem(problem_description, knowledge_results)
        
        # Analyze causes
        causes = await self._analyze_causes(
            problem_description,
            knowledge_results,
            device_info
        )
        
        # Determine severity and complexity
        severity = self._assess_severity(problem_description, causes)
        complexity = self._assess_complexity(problem_description, causes)
        
        # Safety assessment
        requires_backup = any(word in problem_description.lower() 
                            for word in ["format", "reset", "reinstall", "delete"])
        
        safe_to_attempt = not any(word in problem_description.lower()
                                for word in ["smoking", "burning", "sparks", "shock"])
        
        return {
            "problem_category": category,
            "severity": severity,
            "likely_causes": causes,
            "estimated_complexity": complexity,
            "requires_data_backup": requires_backup,
            "safe_to_attempt": safe_to_attempt
        }
    
    async def _rephrase_query(
        self,
        user_query: str,
        device_info: Optional[DeviceInfo]
    ) -> str:
        """
        Convert vague user query into clear technical problem statement
        """
        query_lower = user_query.lower()
        
        # Pattern matching for common issues
        patterns = {
            r"(wifi|wi-fi|internet|network).*(not work|can't connect|won't connect)": 
                "Wi-Fi connectivity issues",
            r"(slow|laggy|sluggish|freeze|frozen)": 
                "Computer performance issues - slow/freezing",
            r"(blue screen|bsod|crash)": 
                "Blue Screen of Death (BSOD) - system crash",
            r"(won't turn on|no power|dead|not starting)": 
                "Device power failure - won't turn on",
            r"(printer).*(not work|won't print|not printing)": 
                "Printer not printing",
            r"(battery).*(drain|dying|fast|quick)": 
                "Battery draining quickly",
            r"(forgot|lost).*(password)": 
                "Password recovery - locked out",
            r"(email).*(not work|can't send|can't receive)": 
                "Email client issues",
            r"(update).*(fail|error|stuck)": 
                "Software update failure",
            r"(virus|malware|infected)": 
                "Potential malware infection",
        }
        
        for pattern, description in patterns.items():
            if re.search(pattern, query_lower):
                if device_info and device_info.device_type:
                    return f"{description} on {device_info.device_type}"
                return description
        
        # Default: return cleaned up version
        return user_query.strip()
    
    def _check_missing_info(
        self,
        user_problem: str,
        device_info: Optional[DeviceInfo]
    ) -> Optional[str]:
        """
        Check if critical information is missing and generate follow-up question
        """
        problem_lower = user_problem.lower()

        # Don't ask for "more info" for greetings/small-talk.
        if self._is_greeting_or_smalltalk(user_problem):
            return None
        
        # If problem is very short, still respond, but ask a targeted clarifier.
        if len(user_problem.split()) < 4:
            return FOLLOW_UP_QUESTIONS["short_problem"]
        
        # Device type can help, but should not block troubleshooting.
        if not device_info or not device_info.device_type:
            if any(word in problem_lower for word in ["computer", "pc", "laptop", "phone"]):
                # Can infer from text
                return None
            return FOLLOW_UP_QUESTIONS["device_and_os"]
        
        # Check for OS if it matters
        if not device_info.os:
            if any(word in problem_lower for word in ["update", "settings", "system"]):
                return FOLLOW_UP_QUESTIONS["os"]
        
        return None
    
    def _format_knowledge_context(self, knowledge_results: List[Dict]) -> str:
        """Format retrieved knowledge for LLM context"""
        if not knowledge_results:
            return "No specific knowledge base matches found. Use general IT support expertise."
        
        context = "Relevant troubleshooting information:\n\n"
        for i, result in enumerate(knowledge_results[:3], 1):
            metadata = result.get("metadata", {})
            context += f"{i}. {result.get('problem', 'Unknown')}\n"
            context += f"   Similarity: {result.get('similarity', 0):.2f}\n"
            
            # Parse data if available
            try:
                if 'data' in metadata:
                    data = eval(metadata['data'])
                    if 'causes' in data:
                        context += f"   Common causes: {', '.join([c['cause'] for c in data['causes'][:2]])}\n"
            except:
                pass
            
            context += "\n"
        
        return context
    
    async def _analyze_causes(
        self,
        problem: str,
        knowledge_results: List[Dict],
        device_info: Optional[DeviceInfo]
    ) -> List[Dict[str, Any]]:
        """
        Analyze and rank potential causes
        """
        causes = []
        
        # Extract causes from knowledge base
        for result in knowledge_results:
            try:
                metadata = result.get("metadata", {})
                if 'data' in metadata:
                    data = eval(metadata['data'])
                    if 'causes' in data:
                        for cause in data['causes']:
                            # Check if already in list
                            if not any(c['cause'] == cause['cause'] for c in causes):
                                causes.append({
                                    "cause": cause['cause'],
                                    "likelihood": cause['likelihood'],
                                    "explanation": f"Common issue for {result.get('problem', 'this problem')}"
                                })
            except Exception as e:
                logger.warning(f"Error parsing cause data: {e}")
        
        # If no causes found, provide generic ones
        if not causes:
            causes = [
                {
                    "cause": "Software configuration issue",
                    "likelihood": "medium",
                    "explanation": "Settings or software may need adjustment"
                },
                {
                    "cause": "Temporary system glitch",
                    "likelihood": "medium",
                    "explanation": "Restart often resolves temporary issues"
                }
            ]
        
        # Sort by likelihood
        likelihood_order = {"high": 3, "medium": 2, "low": 1}
        causes.sort(key=lambda x: likelihood_order.get(x['likelihood'], 0), reverse=True)
        
        return causes[:4]  # Top 4 causes
    
    async def _generate_solution_steps(
        self,
        problem: str,
        causes: List[Dict],
        knowledge_results: List[Dict],
        conversation_history: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Generate step-by-step solutions
        """
        steps = []
        
        # Extract steps from knowledge base
        for result in knowledge_results:
            try:
                metadata = result.get("metadata", {})
                if 'data' in metadata:
                    data = eval(metadata['data'])
                    if 'solutions' in data:
                        for sol in data['solutions']:
                            steps.append({
                                "step_number": sol.get('step', len(steps) + 1),
                                "action": sol.get('action', ''),
                                "explanation": sol.get('why', ''),
                                "risk_level": sol.get('risk_level', 'safe'),
                                "expected_outcome": None,
                                "troubleshooting_tips": []
                            })
                        break  # Use first matching solution set
            except Exception as e:
                logger.warning(f"Error parsing solution data: {e}")
        
        # If no steps found, provide generic troubleshooting
        if not steps:
            steps = [
                {
                    "step_number": 1,
                    "action": "Restart the device",
                    "explanation": "Clears temporary issues and resets system state",
                    "risk_level": "safe",
                    "expected_outcome": "Device functions normally after restart",
                    "troubleshooting_tips": ["Save any open work before restarting"]
                },
                {
                    "step_number": 2,
                    "action": "Check for and install any available updates",
                    "explanation": "Updates often include bug fixes and improvements",
                    "risk_level": "safe",
                    "expected_outcome": "System is up to date and issues are resolved",
                    "troubleshooting_tips": ["Ensure stable internet connection", "Allow time for updates to install"]
                },
                {
                    "step_number": 3,
                    "action": "Review recent changes or new software installations",
                    "explanation": "Problems often correlate with recent changes",
                    "risk_level": "safe",
                    "expected_outcome": "Identify what might have caused the issue",
                    "troubleshooting_tips": ["Consider uninstalling recently added software"]
                }
            ]
        
        # Check what user has already tried
        tried_steps = set()
        for msg in conversation_history:
            if msg.get('role') == 'user':
                content_lower = msg.get('content', '').lower()
                if 'tried' in content_lower or 'already' in content_lower:
                    if 'restart' in content_lower:
                        tried_steps.add('restart')
                    if 'update' in content_lower:
                        tried_steps.add('update')
        
        # Filter out already tried steps
        if tried_steps:
            steps = [s for s in steps if not any(word in s['action'].lower() 
                    for word in tried_steps)]
        
        # Renumber steps
        for i, step in enumerate(steps, 1):
            step['step_number'] = i
        
        return steps[:6]  # Max 6 steps
    
    def _generate_next_steps(
        self,
        solution_steps: List[Dict],
        requires_professional: bool
    ) -> str:
        """
        Generate guidance for what to do if solutions don't work
        """
        if requires_professional:
            return ("If these steps don't resolve the issue, I recommend contacting a "
                   "professional technician. The problem may require hardware repair or "
                   "specialized tools.")
        
        if len(solution_steps) > 3:
            return ("If the above steps don't work, let me know which step you got stuck on "
                   "and I can provide more specific guidance or alternative solutions.")
        
        return ("If these steps don't resolve the issue, please let me know:\n"
                "1. Which step you completed\n"
                "2. What happened when you tried it\n"
                "3. Any error messages you saw\n\n"
                "I'll provide more advanced troubleshooting steps.")
    
    def _categorize_problem(
        self,
        problem: str,
        knowledge_results: List[Dict]
    ) -> str:
        """Categorize the problem type"""
        if knowledge_results and len(knowledge_results) > 0:
            return knowledge_results[0].get("category", "general")
        
        problem_lower = problem.lower()
        if any(word in problem_lower for word in ["wifi", "internet", "network"]):
            return "networking"
        elif any(word in problem_lower for word in ["slow", "freeze", "performance"]):
            return "performance"
        elif any(word in problem_lower for word in ["printer", "keyboard", "mouse"]):
            return "peripherals"
        elif any(word in problem_lower for word in ["phone", "android", "ios"]):
            return "mobile"
        elif any(word in problem_lower for word in ["crash", "error", "blue screen"]):
            return "system"
        else:
            return "general"
    
    def _assess_severity(self, problem: str, causes: List[Dict]) -> str:
        """Assess problem severity"""
        problem_lower = problem.lower()
        
        critical_keywords = ["crash", "lost", "deleted", "corrupted", "smoking", "burning"]
        high_keywords = ["won't turn on", "blue screen", "no power", "dead"]
        
        if any(word in problem_lower for word in critical_keywords):
            return "critical"
        elif any(word in problem_lower for word in high_keywords):
            return "high"
        elif any(c['likelihood'] == 'high' for c in causes):
            return "medium"
        else:
            return "low"
    
    def _assess_complexity(self, problem: str, causes: List[Dict]) -> str:
        """Assess solution complexity"""
        problem_lower = problem.lower()
        
        simple_keywords = ["slow", "wifi", "password", "volume"]
        complex_keywords = ["blue screen", "corrupted", "driver", "registry"]
        
        if any(word in problem_lower for word in complex_keywords):
            return "complex"
        elif any(word in problem_lower for word in simple_keywords):
            return "simple"
        else:
            return "moderate"
