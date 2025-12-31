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

FOLLOW_UP_QUESTION_LIST: list[str] = list(FOLLOW_UP_QUESTIONS.values())

# Representative questions a user can ask the assistant.
# These are intentionally broad (20–30) and cover both known KB topics
# and generic troubleshooting.
USER_QUESTION_LIST: list[str] = [
    "Hi",
    "My Wi‑Fi won’t connect on my Windows laptop.",
    "Internet keeps disconnecting every few minutes.",
    "My PC is running very slow after the last update.",
    "My laptop freezes randomly when I open Chrome.",
    "I got a blue screen (BSOD) and it restarted—what should I do?",
    "The BSOD says DRIVER_IRQL_NOT_LESS_OR_EQUAL.",
    "My printer is connected but not printing anything.",
    "My printer shows Offline and jobs are stuck in the queue.",
    "My phone battery is draining fast even when I’m not using it.",
    "My Android phone won’t charge past 20%.",
    "I forgot my Windows password and I’m locked out.",
    "I can’t send emails from Outlook—messages stay in Outbox.",
    "I’m not receiving any emails on my phone.",
    "Windows Update is stuck at 0% for hours.",
    "My software update fails with an error.",
    "I think my computer has a virus—lots of popups and it’s slow.",
    "My browser keeps redirecting to weird sites.",
    "My computer won’t turn on at all—no lights.",
    "My laptop is overheating and the fan is very loud.",
    "There’s no sound coming from my laptop speakers.",
    "My microphone isn’t working in Zoom.",
    "My webcam is not detected.",
    "Bluetooth won’t connect to my headphones.",
    "My keyboard types the wrong characters.",
    "My external hard drive isn’t showing up.",
    "I’m running out of disk space—how do I free it up?",
    "My PC is very slow to boot.",
    "My screen is flickering on Windows.",
    "My laptop is smoking.",
]

# Backwards-compatible name used by existing code/tests.
ALL_QUESTIONS: list[str] = [*USER_QUESTION_LIST, *FOLLOW_UP_QUESTION_LIST]

# Explicit combined list for tooling.
ALL_TEST_QUESTIONS: list[str] = ALL_QUESTIONS
