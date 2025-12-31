from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from api.config import settings
from services.llm_service import LLMService
from services.rag_service import RAGService
from services.reasoning_engine import ReasoningEngine
from services.question_catalog import (
    USER_QUESTION_LIST,
    FOLLOW_UP_QUESTION_LIST,
)


async def build_questions_txt_content() -> str:
    """Generate deterministic Q/A content for `questions.txt`.

    This forces deterministic mode (no remote LLM calls) so the output is stable
    and testable.
    """
    # Force deterministic fallback mode even if a user has keys locally.
    settings.openai_api_key = ""
    settings.anthropic_api_key = ""

    rag = RAGService()
    await rag.initialize()
    llm = LLMService()
    engine = ReasoningEngine(rag, llm)

    sections: list[str] = []
    sections.append("# Tech Mentor - Assistant Question List")
    sections.append("")
    sections.append(
        "This file lists questions you can ask the assistant (user prompts) and the follow-up questions the assistant may ask you."
    )
    sections.append("Every entry below is verified to produce a non-empty response and a `reasoning_type`.")
    sections.append("")

    async def _append_verified_block(kind: str, idx: int, question: str) -> None:
        result = await engine.diagnose_and_solve(
            user_problem=question,
            conversation_history=[],
            device_info=None,
            technical_level="beginner",
        )

        response_text = (result.get("response") or "").strip()
        reasoning_type = (result.get("reasoning_type") or "").strip()
        follow_up_question = (result.get("follow_up_question") or "").strip()

        if not response_text:
            raise AssertionError(f"Missing response for {kind} Q{idx}: {question}")
        if not reasoning_type:
            raise AssertionError(f"Missing reasoning_type for {kind} Q{idx}: {question}")

        sections.append(f"{kind} Q{idx}: {question}")
        sections.append(f"Reasoning type: {reasoning_type}")
        sections.append("Response:")
        sections.append(response_text)
        sections.append("Assistant follow-up question (if any):")
        sections.append(follow_up_question if follow_up_question else "(None)")
        sections.append("")
        sections.append("---")
        sections.append("")

    sections.append("## User Questions")
    sections.append("")
    for idx, question in enumerate(USER_QUESTION_LIST, start=1):
        await _append_verified_block("User", idx, question)

    sections.append("## Assistant Follow-up Questions")
    sections.append("")
    for idx, question in enumerate(FOLLOW_UP_QUESTION_LIST, start=1):
        await _append_verified_block("Follow-up", idx, question)

    return "\n".join(sections).rstrip() + "\n"


def write_questions_txt(repo_root: Path) -> Path:
    """Write `questions.txt` to the repo root."""
    output_path = repo_root / "questions.txt"
    content = asyncio.run(build_questions_txt_content())
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main(argv: Optional[list[str]] = None) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    write_questions_txt(repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
