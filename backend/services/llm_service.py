"""
LLM Service - Integration with various language models
"""
from typing import List, Dict, Optional, Any
import json
from loguru import logger

from api.config import settings

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMService:
    """Service for interacting with Language Models"""
    
    def __init__(self):
        self.provider = settings.default_llm_provider
        self.model = settings.default_model

        def _is_real_api_key(value: str) -> bool:
            if not value:
                return False
            v = value.strip()
            if not v:
                return False
            # Common placeholders
            lowered = v.lower()
            if lowered in {"your_openai_api_key_here", "your_anthropic_api_key_here", "changeme"}:
                return False
            # Heuristic: real OpenAI keys almost always start with "sk-" (including newer variants).
            if lowered.startswith("sk-"):
                return True
            # If user has a non-standard key format, allow it only if it looks non-placeholder.
            return len(v) >= 20 and " " not in v and "_key_here" not in lowered
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None

        if self.provider == "openai" and OPENAI_AVAILABLE and _is_real_api_key(settings.openai_api_key):
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE and _is_real_api_key(settings.anthropic_api_key):
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        else:
            logger.warning(f"LLM provider {self.provider} not configured/available, using deterministic fallback mode")
    
    async def generate_completion(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a completion from the LLM
        
        Args:
            system_prompt: System instructions
            user_message: User's input
            conversation_history: Previous messages
            temperature: Sampling temperature
            max_tokens: Maximum response length
        
        Returns:
            Generated response text
        """
        try:
            if self.provider == "openai" and self.openai_client:
                return await self._generate_openai(
                    system_prompt, user_message, conversation_history,
                    temperature, max_tokens
                )
            elif self.provider == "anthropic" and self.anthropic_client:
                return await self._generate_anthropic(
                    system_prompt, user_message, conversation_history,
                    temperature, max_tokens
                )
            else:
                # Fallback to rule-based response
                return await self._generate_fallback(user_message)
                
        except Exception as e:
            # If the remote LLM call fails (bad key, network, rate limits), do not return a scary error.
            # Return a best-effort fallback response instead.
            logger.exception(f"Error generating completion, falling back: {e}")
            return await self._generate_fallback(user_message)
    
    async def _generate_openai(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate completion using OpenAI"""
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def _generate_anthropic(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate completion using Anthropic Claude"""
        messages = []
        
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.anthropic_client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.content[0].text
    
    async def _generate_fallback(self, user_message: str) -> str:
        """Fallback response when no LLM is available"""
        logger.warning("Using fallback response - no LLM configured")
        
        message_lower = user_message.lower()
        
        # Simple keyword-based responses
        if any(word in message_lower for word in ["wifi", "internet", "network", "connect"]):
            return """I understand you're having network connectivity issues. Here are some basic steps:

1. **Check Wi-Fi is enabled**: Make sure airplane mode is off and Wi-Fi is turned on
2. **Restart your router**: Unplug it for 30 seconds, then plug back in
3. **Forget and reconnect**: Remove the network from your device and reconnect with the password
4. **Check other devices**: See if other devices can connect to rule out router issues

If these don't work, the problem might be with your ISP or require professional help."""

        elif any(word in message_lower for word in ["slow", "laggy", "freeze", "performance"]):
            return """For performance issues, try these steps:

1. **Check resource usage**: Open Task Manager (Ctrl+Shift+Esc) to see what's using CPU/RAM
2. **Close unnecessary programs**: End tasks that you don't need
3. **Restart your computer**: This clears temporary issues
4. **Check disk space**: Make sure you have at least 15% free space
5. **Scan for malware**: Run Windows Defender or your antivirus

Let me know which step you're on if you need more guidance!"""

        elif any(word in message_lower for word in ["won't turn on", "no power", "dead"]):
            return """If your device won't turn on:

1. **Check power source**: Verify the power cable is connected and outlet works
2. **Check for indicator lights**: Any LEDs or signs of power?
3. **Try hard reset**: 
   - Unplug power
   - Remove battery (if possible)
   - Hold power button for 30 seconds
   - Reconnect and try again

4. **Test with different adapter**: If available, try another power adapter

⚠️ If none of this works, it may be a hardware failure requiring professional repair."""

        else:
            return """I'm running in limited mode without full AI capabilities. To help you effectively, I need an API key configured.

However, I can still provide general guidance:

1. **Describe your problem in detail**: What device? What's happening? When did it start?
2. **What have you tried**: This helps avoid repeating steps
3. **Any error messages**: Exact error text is very helpful

For now, try these universal troubleshooting steps:
- Restart the device
- Check all cables/connections
- Update software/drivers
- Search for the specific error message online

Please configure an OpenAI or Anthropic API key for full assistant capabilities."""
    
    def format_system_prompt(
        self,
        knowledge_context: str,
        device_info: Optional[Dict] = None,
        technical_level: str = "beginner"
    ) -> str:
        """
        Create the system prompt with context
        
        Args:
            knowledge_context: Retrieved knowledge from RAG
            device_info: User's device information
            technical_level: User's technical expertise level
        
        Returns:
            Formatted system prompt
        """
        prompt = """You are an expert IT Support Technical Assistant with 10+ years of experience. Your goal is to diagnose and solve technology problems through logical reasoning.

MANDATORY RESPONSE STRUCTURE:
1. **Problem Understanding**: Rephrase the user's issue clearly
2. **Likely Causes**: List 2-4 potential causes (most likely first)
3. **Step-by-Step Solution**: Numbered steps from simplest to advanced
4. **Next Steps**: What to do if the solution doesn't work
5. **Follow-up Question**: Only if critical info is missing

REASONING RULES:
- Use elimination logic (try simple fixes first)
- Explain why each step matters
- Warn before any risky action (data loss, system changes)
- If hardware repair is needed, say so clearly
- Track what the user has already tried to avoid repetition
"""

        # Add technical level adjustment
        if technical_level == "beginner":
            prompt += "\n- Avoid technical jargon, use simple language\n- Provide detailed explanations\n- Include screenshots guidance when helpful"
        elif technical_level == "intermediate":
            prompt += "\n- Use moderate technical terms\n- Balance detail with brevity\n- Assume basic computer literacy"
        else:  # advanced
            prompt += "\n- Use technical terminology freely\n- Be concise, assume expertise\n- Include advanced troubleshooting options"
        
        # Add device context
        if device_info:
            prompt += f"\n\nUSER'S DEVICE:\n"
            if device_info.get("device_type"):
                prompt += f"- Type: {device_info['device_type']}\n"
            if device_info.get("os"):
                prompt += f"- OS: {device_info['os']}\n"
            if device_info.get("os_version"):
                prompt += f"- Version: {device_info['os_version']}\n"
        
        # Add knowledge base context
        if knowledge_context:
            prompt += f"\n\nKNOWLEDGE BASE CONTEXT:\n{knowledge_context}\n"
        
        prompt += "\n\nIMPORTANT: Always maintain a helpful, patient tone. If you're unsure, ask clarifying questions rather than guessing."
        
        return prompt
