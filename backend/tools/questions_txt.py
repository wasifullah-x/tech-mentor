from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from api.config import settings
from services.llm_service import LLMService
from services.rag_service import RAGService
from services.reasoning_engine import ReasoningEngine
from services.question_catalog import ALL_QUESTIONS


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
        "This file lists every follow-up question the assistant may ask, and a verified sample response for each."
    )
    sections.append("")

    for idx, question in enumerate(ALL_QUESTIONS, start=1):
        result = await engine.diagnose_and_solve(
            user_problem=question,
            conversation_history=[],
            device_info=None,
            technical_level="beginner",
        )

        response_text = (result.get("response") or "").strip()
        reasoning_type = (result.get("reasoning_type") or "").strip()

        sections.append(f"Q{idx}: {question}")
        sections.append(f"Reasoning type: {reasoning_type if reasoning_type else '(missing)'}")
        sections.append("Response:")
        sections.append(response_text if response_text else "(missing)")
        sections.append("")
        sections.append("---")
        sections.append("")

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
