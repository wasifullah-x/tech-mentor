import pytest
from pathlib import Path

from tools.questions_txt import build_questions_txt_content
from services.question_catalog import USER_QUESTION_LIST, FOLLOW_UP_QUESTION_LIST


@pytest.mark.asyncio
async def test_questions_txt_content_has_all_questions_and_responses():
    content = await build_questions_txt_content()

    # Every question should appear, and each should have a reasoning type + response section.
    for q in [*USER_QUESTION_LIST, *FOLLOW_UP_QUESTION_LIST]:
        assert q in content

    # Ensure we have a reasonable set of user questions (20–30+ expected).
    assert len(USER_QUESTION_LIST) >= 20

    assert "Reasoning type:" in content
    assert "Response:" in content


@pytest.mark.asyncio
async def test_repo_questions_txt_is_up_to_date():
    # If this fails, run (from backend/): python -m tools.questions_txt
    generated = await build_questions_txt_content()

    repo_root_questions = Path(__file__).resolve().parents[2] / "questions.txt"
    existing = repo_root_questions.read_text(encoding="utf-8")

    assert existing == generated
