"""Catalog of all follow-up questions the assistant may ask.

Keeping these strings in one place ensures:
- `questions.txt` stays in sync with runtime behavior
- tests can verify coverage without brittle string scraping
"""

from __future__ import annotations

FOLLOW_UP_QUESTIONS: dict[str, str] = {
    "onboarding": "What can I help you fix today?",
    "short_problem": (
        "Quick clarifier: what device/OS is this on, and what exactly happens (any exact error message)?"
    ),
    "device_and_os": "What type of device is this (laptop/desktop/phone/printer), and what OS are you using?",
    "os": "What operating system are you using? (Windows, macOS, Android, iOS, Linux)",
}

ALL_QUESTIONS: list[str] = list(FOLLOW_UP_QUESTIONS.values())
