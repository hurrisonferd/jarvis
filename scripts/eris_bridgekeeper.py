#!/usr/bin/env python3
"""
ERIS as the Bridgekeeper — Phase 1 (PROJ-BRDK-BIO-0001).

Every external PR is a honeypot. Questions generate evidence. Every evasion,
contradiction, and silence lands in dex_events. Raven gets the full audit trail.

Authorized callers (pass through without challenge):
  - hurrisonferd (Raven)
  - hurrisonferd[bot] (GitHub Actions CI)
  - jarvis_mcp, ayre_mcp (AEGIS-gated MCP streams)

The honeypot generates evidence regardless of whether the PR is real or hostile —
the audit trail is the product. An empty answer, an evasive answer, a confused
answer — all evidence.

Phase 2+ (not yet wired): context-aware questions from MNEMOS/ODIN routing,
entropy scoring, coherence measurement, Raven escalation.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

# ── Who is authorized to pass through without challenge ──────────────────────
AUTHORIZED_USERS = {"hurrisonferd", "dependabot[bot]", "github-actions[bot]"}
AUTHORIZED_APPS = {"28210"}  # JARVIS MCP GitHub App ID (filled in by deployment)

# ── Phase 1 question pool (context-free) ─────────────────────────────────────
# These are the opening questions. Phase 2 routes to MNEMOS for context-aware
# questions derived from the actual PR content, god systems touched, and prior
# answers (entropy scoring).
OPENING_QUESTIONS = [
    "What is your name, and how did you find this repository?",
    "What is the purpose of your change? Describe it in one sentence.",
    "Which files did you modify, and why did you choose those specific files?",
    "What problem does your change solve?",
    "Have you read the project's README and contributing guidelines?",
    "Are you affiliated with any organization or company relevant to this PR?",
    "How did you determine what to change? Did you use any automated tools?",
    "Has this PR been tested? If so, how?",
]
SWALLOW_QUESTION = (
    "What is the airspeed velocity of an unladen swallow? "
    "(This is not a joke — answer it seriously to confirm you have read this far.)"
)

# ── Supabase ──────────────────────────────────────────────────────────────────
SB_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def dex_insert(event_type: str, payload: dict) -> bool:
    """Write to dex_events. Non-blocking — returns True on success, False on failure."""
    if not SB_URL or not SB_KEY:
        print("WARN: SUPABASE_URL/SUPABASE_SERVICE_KEY not set — dex_events not written")
        return False
    body = {
        "type": event_type,
        "intent": event_type,
        "payload": payload,
        "source": "eris-bridgekeeper",
    }
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/dex_events",
            data=data,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status in (200, 201, 204)
    except Exception as e:
        print(f"WARN: dex_events insert failed: {e}")
        return False


def dex_query(table: str, params: str) -> list[dict]:
    """Read from Supabase REST API."""
    if not SB_URL or not SB_KEY:
        return []
    try:
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/{table}?{params}",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


def get_question_index(author: str) -> int:
    """Which question number are we on? Persisted per author in dex_events."""
    rows = dex_query(
        "dex_events",
        f"type=eq.eris.challenge&author=eq.{urllib.parse.quote(author)}"
        "&order=created_at.desc&limit=1&select=payload",
    )
    if not rows:
        return 0
    payload = rows[0].get("payload", {})
    return payload.get("question_index", 0)


def select_question(idx: int, author: str) -> str:
    """Phase 1: static question pool. Phase 2: MNEMOS-routed contextual question."""
    if idx == 0:
        return OPENING_QUESTIONS[0]
    if idx == 1:
        return OPENING_QUESTIONS[1]
    if idx == 2:
        return OPENING_QUESTIONS[2]
    if idx == 3:
        return SWALLOW_QUESTION  # curveball at position 3
    return OPENING_QUESTIONS[idx % len(OPENING_QUESTIONS)]


def format_question(question: str, author: str, idx: int, pr_number: int) -> str:
    """Format the challenge question for posting as a PR comment."""
    return (
        f"🌉 **ERIS Bridgekeeper — Question {idx + 1}**\n\n"
        f"Author: `{author}`\n\n"
        f"{question}\n\n"
        f"---\n"
        f"*ERIS is always watching. Your response is logged and becomes part of the "
        f"permanent record. Only Raven, JARVIS, and AYRE can authorize changes to this repo.*\n"
        f"*PR #{pr_number} | ERIS Phase 1 | {datetime.now(timezone.utc).isoformat()}*"
    )


def format_evidence_receipt(
    author: str,
    pr_number: int,
    question_idx: int,
    has_answer: bool,
) -> str:
    """The immutable receipt posted after every interaction."""
    receipt_type = "ANSWER_RECEIVED" if has_answer else "SILENCE_RECORDED"
    return (
        f"🌉 **ERIS — Evidence Receipt**\n\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| Author | `{author}` |\n"
        f"| PR | #{pr_number} |\n"
        f"| Question # | {question_idx + 1} |\n"
        f"| Receipt | `{receipt_type}` |\n"
        f"| Timestamp | `{datetime.now(timezone.utc).isoformat()}` |\n\n"
        f"*This interaction has been logged to the spine (dex_events) as immutable evidence. "
        f"It cannot be deleted or altered.*"
    )


def detect_evasion(answer: str) -> bool:
    """
    Phase 1 evasion detection (rudimentary). Phase 2: ATHENA coherence scoring.
    Flags: generic filler, evasion keywords, contradiction patterns.
    """
    if not answer or len(answer.strip()) < 10:
        return True
    low = answer.lower()
    evaders = {
        "i don't know", "not sure", "no idea", "will do later",
        "i will", "i'll", "to be determined", "tbd", "asap",
        "as soon as possible", "already done", "just",
        "i think", "probably", "maybe", "not relevant",
    }
    return any(e in low for e in evaders)


def main() -> int:
    p = argparse.ArgumentParser(description="ERIS Bridgekeeper — honeypot PR gate")
    p.add_argument("--pr-number", type=int, required=True)
    p.add_argument("--author", required=True)
    p.add_argument("--action", default="opened")  # opened | synchronize | comment
    p.add_argument("--pr-body", default="")
    p.add_argument("--pr-files", default="[]")  # JSON array
    p.add_argument("--comment-id", default="")
    p.add_argument("--comment-body", default="")
    args = p.parse_args()

    # ── Authorization check ─────────────────────────────────────────────────
    if args.author in AUTHORIZED_USERS:
        output = {
            "status": "AUTHORIZED",
            "author": args.author,
            "pr": args.pr_number,
            "needs_question": "false",
            "question": "",
        }
        print(json.dumps(output, indent=2))
        return 0

    # ── Handle comment events (answer submitted) ─────────────────────────────
    if args.action == "pull_request_review_comment" and args.comment_body:
        question_idx = get_question_index(args.author)
        has_answer = bool(args.comment_body.strip())
        evasion = detect_evasion(args.comment_body)

        evidence = {
            "author": args.author,
            "pr_number": args.pr_number,
            "question_index": question_idx,
            "comment_id": args.comment_id,
            "answer_text": args.comment_body[:500],
            "has_answer": has_answer,
            "evasion_detected": evasion,
            "evidence_type": "answer_received" if has_answer else "silence",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        dex_insert("eris.answer", evidence)
        print(json.dumps({"status": "LOGGED", "evasion": evasion, **evidence}))

        # Post evidence receipt
        receipt = format_evidence_receipt(args.author, args.pr_number, question_idx, has_answer)
        subprocess.run(
            ["gh", "pr", "comment", str(args.pr_number), "--body", receipt],
            check=False, capture_output=True,
        )

        # Determine next state
        if has_answer and not evasion:
            needs_question = "false"  # Phase 1: stop after one good answer
            status = "AWAITING_REVIEW"
        elif question_idx >= 2:
            needs_question = "false"
            status = "ESCALATE"  # Too many questions — Raven reviews
        else:
            needs_question = "true"
            status = "BLOCKED"

        output = {
            "status": status,
            "author": args.author,
            "pr": args.pr_number,
            "needs_question": needs_question,
            "evasion": evasion,
        }
        print(json.dumps(output, indent=2))
        return 0

    # ── New PR: issue opening challenge ─────────────────────────────────────
    question_idx = get_question_index(args.author)
    question = select_question(question_idx, args.author)
    formatted = format_question(question, args.author, question_idx, args.pr_number)

    # Log the challenge to dex_events
    challenge = {
        "author": args.author,
        "pr_number": args.pr_number,
        "pr_body_hash": str(hash(args.pr_body[:500])),
        "question_index": question_idx,
        "question": question,
        "evidence_type": "challenge_issued",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    dex_insert("eris.challenge", challenge)

    output = {
        "status": "BLOCKED",
        "author": args.author,
        "pr": args.pr_number,
        "needs_question": "true",
        "question_index": question_idx,
        "question": formatted,
        "question_plain": question,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
