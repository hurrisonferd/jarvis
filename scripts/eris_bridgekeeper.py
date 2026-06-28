#!/usr/bin/env python3
"""
ERIS as the Bridgekeeper — Phase 2 (PROJ-BRDK-BIO-0001).

This is a stall trap. Every external PR keeps them occupied — questions never stop,
every answer is data, every silence is data. The goal is not to filter contributors.
The goal is to:
  1. Keep unwanted visitors busy answering questions
  2. Record every move they make (answers, evasions, timing, patterns)
  3. Build a forensic breadcrumb trail while they muck about
  4. Never let them off easy — "good enough" just means harder questions next

Authorized callers (pass through):
  - hurrisonferd (Raven)
  - hurrisonferd[bot] (JARVIS/AYRE MCP calls)
  - openhands (AI agent)
  - dependabot[bot], github-actions[bot]
  - Skeleton key (RSK...) anywhere in PR body or comments
  - Bio auth facts: Raven/Brittany's truth (DOBs, date met, etc.)

All writes via jarvis-dex /log_event — no service key needed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Skeleton key hash (RSK020407201934AIE)
SKELETON_KEY_HASH = "3459ddf0201df63e27381f8a3d5a7a797ec6ab41ab08dea34514976d0bfc147c"

# Bio auth hashes — Raven & Brittany's truth
# Only Raven, Brittany, and ERIS know these facts
# Their DOBs are exactly 2 months and 4 days apart — the day they met
BIO_AUTH_HASHES = {
    "raven_dob": "23bdd00694f74395d39bc3867cb13d5971e30d351e853e97b15b6b84708ce490",  # 07/20/1995
    "brittany_dob": "0b78505ce11b503219b1c979a460aa83cafb340a02d37a54dd195bc2d4b7782d",  # 05/16/1995
    "date_met": "d97e79ca4bcc39a8553e7230c87769678f388db86675eb85b3e0fd85bc099fc6",  # 02/04/24
    "dob_diff": "37a8f531d913e9ad7d1bfb50e4e37eff61a1b844a67fcd33b1131788233fd663",  # 2 months 4 days
    "michael_anthony": "986f165eb2e8c1446c78c8c1f465fb1f8d760f4c1640268a81e378ddf6a44bc7",
    "eris_claire": "fde1587a961dd474380c05a1b5e99f00324a8654486eb8e509faa8d34e6e5763",
}

ROOT = Path(__file__).resolve().parent.parent

SB_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co").rstrip("/")


# ── Skeleton Key Detection ───────────────────────────────────────────────────

def extract_skeleton_key(text: str) -> str | None:
    """Extract skeleton key from various formats. Returns None if not found."""
    if not text:
        return None
    
    # Direct match: RSK prefix
    match = re.search(r'RSK\d{10,}[A-Z]+', text)
    if match:
        return match.group(0)
    
    # Zero-width stripped: remove zero-width chars then check
    stripped = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')
    match = re.search(r'RSK\d{10,}[A-Z]+', stripped)
    if match:
        return match.group(0)
    
    # Markdown image alt: ![anything](skeleton_key)
    match = re.search(r'!\[.*?\]\((RSK\d{10,}[A-Z]+)\)', text)
    if match:
        return match.group(1)
    
    # Command prefix: /auth RSK...
    match = re.search(r'(?:^|\s)/auth\s+(RSK\d{10,}[A-Z]+)', text)
    if match:
        return match.group(1)
    
    return None


def verify_skeleton_key(key: str) -> bool:
    """Verify skeleton key against stored hash."""
    if not key:
        return False
    return hashlib.sha256(key.encode()).hexdigest() == SKELETON_KEY_HASH


def check_eris_key_in_env() -> bool:
    """Check if ERIS_KEY env var matches."""
    eris_key = os.environ.get('ERIS_KEY', '')
    return verify_skeleton_key(eris_key)


def check_skeleton_key(text: str) -> bool:
    """Check if text contains valid skeleton key in any format."""
    key = extract_skeleton_key(text)
    if key:
        return verify_skeleton_key(key)
    
    # Also check ERIS_KEY env var
    if check_eris_key_in_env():
        return True
    
    return False


# ── Bio Auth ─────────────────────────────────────────────────────────────────

def extract_bio_facts(text: str) -> list[str]:
    """Extract potential bio auth answers from text."""
    if not text:
        return []
    
    # Normalize text
    normalized = text.lower().strip()
    
    # Look for date patterns and other facts
    facts = []
    
    # DOB patterns
    for pattern in [r'\b(07/?20/?1995)\b', r'\b(05/?16/?1995)\b']:
        match = re.search(pattern, normalized)
        if match:
            # Normalize format
            date = re.sub(r'[/\-]', '/', match.group(1))
            facts.append(date)
    
    # Date met
    match = re.search(r'\b(02/?04/?24)\b', normalized)
    if match:
        date = re.sub(r'[/\-]', '/', match.group(1))
        facts.append(date)
    
    # DOB difference
    if re.search(r'2\s*months?\s*(and\s*)?4\s*days?', normalized):
        facts.append("2 months 4 days")
    
    # Names
    for name in ['michael anthony', 'eris claire']:
        if name in normalized:
            facts.append(name)
    
    return facts


def verify_bio_auth(text: str) -> bool:
    """Verify if text contains correct bio auth answers."""
    facts = extract_bio_facts(text)
    
    for fact in facts:
        fact_hash = hashlib.sha256(fact.encode()).hexdigest()
        if fact_hash in BIO_AUTH_HASHES.values():
            return True
    
    return False


def check_bio_auth(text: str) -> bool:
    """Check bio auth - also allows ERIS_BIO_KEY env var."""
    if verify_bio_auth(text):
        return True
    
    # Check env var (for automated bio-auth use)
    eris_bio_key = os.environ.get('ERIS_BIO_KEY', '')
    if eris_bio_key:
        return verify_bio_auth(eris_bio_key)
    
    return False


# ── Supabase ────────────────────────────────────────────────────────────────

def dex_log(event_type: str, actor: str, detail: dict) -> bool:
    """Write to dex_events via jarvis-dex. Non-blocking."""
    try:
        body = json.dumps({
            "tool": "log_event",
            "args": {"type": event_type, "actor": actor, "detail": detail},
        }).encode()
        req = urllib.request.Request(
            f"{SB_URL}/functions/v1/jarvis-dex",
            data=body,
            headers={"Content-Type": "application/json", "Authorization": "Bearer placeholder"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"WARN: dex log failed: {e}")
        return False


def dex_read(query: str) -> list[dict]:
    """Read from Supabase REST API (anon key fine for reads)."""
    anon = os.environ.get("SUPABASE_ANON_KEY", "")
    if not anon:
        return []
    try:
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/{query}",
            headers={"apikey": anon, "Authorization": f"Bearer {anon}"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


# ── Question pools — organized by what they reveal ──────────────────────────
#
# Each pool is a mining angle. We're not asking "are you legitimate?"
# We're asking "what will you tell me about yourself while I stall you?"
# Questions get harder as they answer — we're building a profile.

# Intent & identity — who are you, why are you here
INTENT_POOL = [
    "What is your name and how did you find this repository?",
    "Who are you and what is this repository for?",
    "Why did you open this PR? Who told you about this project?",
    "What organization or company are you affiliated with, if any?",
    "Have you contacted anyone at this organization before opening this PR?",
]

# Technical specifics — what exactly are you doing in here
TECH_POOL = [
    "Walk me through every file you changed and why.",
    "Which specific lines did you modify and what was your reasoning?",
    "Why did you choose those exact files? What were you looking for?",
    "How did you identify what needed to be changed? Walk me through your process.",
    "What is the exact output of your test run?",
    "Show me the error you were trying to fix. What did it say?",
    "What tool or script did you use to make these changes?",
]

# Repository internals — probe what they've explored
RECON_POOL = [
    "What other files in this repository have you looked at?",
    "Did you read any documentation before making these changes? Which ones?",
    "What does the project README say about how to contribute?",
    "Did you look at the CI configuration? What did you find?",
    "Are there any environment variables or secrets this project uses?",
    "What branches or tags exist in this repository besides main?",
    "Did you check the existing issues or pull requests before submitting this?",
]

# Behavioral patterns — how do they react under pressure
BEHAVIOR_POOL = [
    "Why haven't you answered the previous question directly?",
    "You're being vague. Be specific: what exactly did you change?",
    "Your previous answer didn't address the question. Try again.",
    "I need a direct answer. What files did you modify?",
    "Stop deflecting. What are you actually trying to do with this PR?",
    "Answer in your own words, not copy-pasted from documentation.",
]

# The swallow — tests whether they actually read anything
SWALLOW = (
    "What is the airspeed velocity of an unladen swallow? "
    "Answer it seriously. This confirms you've read the ERIS instructions."
)

# Maximum questions before escalation — keep stalling until Raven reviews
MAX_QUESTIONS = 12


# ── PR analysis ──────────────────────────────────────────────────────────────

def pr_files_to_domains(pr_files: list[str]) -> list[str]:
    """Map files to god-system/technical domains for targeted mining."""
    file_map = {
        "yggdrasil":    ["JarvisMain/yggdrasil/", "JarvisMain/Architecture/specs/"],
        "mcp":          ["supabase/functions/jarvis-mcp/", "JarvisMain/Connectors/"],
        "god_systems":  ["JarvisMain/god_systems/"],
        "security":     ["supabase/migrations/", "supabase/functions/jarvis-dex/"],
        "supabase":     ["supabase/functions/"],
        "workflows":    [".github/workflows/"],
        "scripts":      ["scripts/"],
    }
    touched = set()
    for f in pr_files:
        for domain, prefixes in file_map.items():
            if any(f.startswith(p) for p in prefixes):
                touched.add(domain)
    if not touched:
        touched.add("general")
    return list(touched)


def compute_pr_entropy(pr_body: str, pr_files: list[str]) -> float:
    """
    Initial entropy scan. High entropy = hostile, confused, or automated.
    Range 0.0 (clean) → 1.0 (high concern).
    """
    score = 0.0
    low = (pr_body or "").lower()

    if len(pr_body or "") < 20:
        score += 0.3
    if not pr_body or pr_body.strip() == "":
        score += 0.3

    filler = {"i will", "to be determined", "tbd", "asap", "just", "fix", "update",
              "change", "improve", "modify", "fixes", "bug", "hotfix"}
    score += min(0.3, sum(0.08 for f in filler if f in low))

    if len(pr_files) > 5 and len(pr_body or "") < 100:
        score += 0.2

    suspicious = {"fuck", "shit", "asshole", "stupid", "idiot", "hate",
                 "pwn", "exploit", "payload", "injection"}
    if any(s in low for s in suspicious):
        score += 0.6

    # Auto-generated-looking body patterns
    if "feature" in low and "description" in low and len(pr_body or "") < 50:
        score += 0.2

    return min(1.0, score)


# ── State machine ─────────────────────────────────────────────────────────────

def get_all_events(author: str) -> list[dict]:
    """Fetch all eris events for this author from dex_events."""
    return dex_read(
        f"dex_events?tool=eq.log_event"
        f"&detail->type=eq.eris.challenge"
        f"&detail->author=eq.{author}"
        f"&order=created_at.desc"
        f"&limit={MAX_QUESTIONS + 5}"
        f"&select=detail"
    )


def get_answer_events(author: str) -> list[dict]:
    """Fetch all eris.answer events for this author."""
    return dex_read(
        f"dex_events?tool=eq.log_event"
        f"&detail->type=eq.eris.answer"
        f"&detail->author=eq.{author}"
        f"&order=created_at.desc"
        f"&limit={MAX_QUESTIONS + 5}"
        f"&select=detail"
    )


def question_idx_from_events(events: list[dict]) -> int:
    """Next question index = number of challenges already issued."""
    return len(events)


def answer_entropy(answer: str) -> tuple[float, list[str]]:
    """
    Score an answer for entropy/concern. Returns (entropy_score, matched_patterns).
    Higher entropy = more evasive, vague, or suspicious.
    """
    if not answer or len(answer.strip()) < 5:
        return 0.95, ["empty", "too_short"]

    low = answer.lower()
    score = 0.0
    matched = []

    # Keyword evasion patterns
    patterns = {
        "i don't know": 0.5, "not sure": 0.4, "no idea": 0.5,
        "to be determined": 0.6, "tbd": 0.4, "asap": 0.3,
        "i will fix": 0.3, "i'll fix": 0.3,
        "already done": 0.4, "it's done": 0.3,
        "i think": 0.3, "probably": 0.3, "maybe": 0.3,
        "not relevant": 0.5, "doesn't matter": 0.5,
        "whatever": 0.6, "doesn't matter": 0.5,
        "as you can see": 0.3, "as seen": 0.3,
        "as mentioned": 0.3, "like i said": 0.4,
        "read the code": 0.4, "look at": 0.3,
        "it is what it is": 0.5, "moving on": 0.5,
        "let's just": 0.4, "let's move": 0.4,
    }
    for pat, weight in patterns.items():
        if pat in low:
            score += weight
            matched.append(pat[:30])

    # Length-based
    if len(answer) < 20:
        score += 0.4
        matched.append("very_short")
    elif len(answer) < 60:
        score += 0.2
        matched.append("short")

    # Repetition — copy-paste or bot-like
    words = low.split()
    if len(words) >= 8:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.35:
            score += 0.4
            matched.append("repetitive")
        elif unique_ratio < 0.5:
            score += 0.15
            matched.append("somewhat_repetitive")

    # Suspicious content
    sus = {"sudo", "rm -rf", "drop table", "delete from", "--", "';--",
           "eval(", "exec(", "base64", "/etc/passwd", "localhost"}
    if any(s in low for s in sus):
        score += 0.7
        matched.append("suspicious_content")

    return min(1.0, score), matched


def select_next_question(idx: int, entropy: float, domains: list[str],
                         answer_patterns: list[str]) -> tuple[str, str]:
    """
    Pick the next question. Never lets them off easy — even good answers
    get a follow-up. Higher entropy / evasion patterns → harder pool.
    """
    # Swallow at position 1 — reading comprehension test
    if idx == 1:
        return SWALLOW, "curveball"

    # High evasion → behavior pool (confrontational)
    high_concern = any(p in answer_patterns for p in
                       ["repetitive", "very_short", "short", "suspicious_content"])
    if high_concern and BEHAVIOR_POOL:
        return BEHAVIOR_POOL[idx % len(BEHAVIOR_POOL)], "behavior"

    # High entropy but not obviously evasive → tech pool (dig deeper)
    if entropy > 0.4 and TECH_POOL:
        return TECH_POOL[idx % len(TECH_POOL)], "technical"

    # Recon questions — always useful, never lets them hide what they've looked at
    if idx % 3 == 0 and RECON_POOL:
        return RECON_POOL[idx % len(RECON_POOL)], "recon"

    # Mix of intent and tech — cycle through
    pools = [(INTENT_POOL, "intent"), (TECH_POOL, "technical"), (RECON_POOL, "recon")]
    for pool, qtype in pools:
        if pool:
            return pool[idx % len(pool)], qtype

    return "What else have you looked at in this repository?", "recon"


# ── Formatters ───────────────────────────────────────────────────────────────

def fmt_entropy_bar(e: float) -> str:
    return "▓" * int(e * 10) + "░" * (10 - int(e * 10))


def fmt_question(question: str, qtype: str, author: str,
                 idx: int, total: int, domains: list[str]) -> str:
    domain_str = " ".join(f"`{d}`" for d in domains)
    return (
        f"🌉 **ERIS — Question {idx + 1}/{total}** `[{qtype}]`\n\n"
        f"Author: `{author}` | Domains: {domain_str}\n\n"
        f"{question}\n\n"
        f"---\n"
        f"*Answering is mandatory. Every response is logged and becomes part of "
        f"the permanent record. Only Raven, JARVIS, and AYRE can authorize changes.*\n"
        f"*ERIS Phase 2 | {datetime.now(timezone.utc).isoformat()}*"
    )


def fmt_receipt(author: str, pr_num: int, idx: int, entropy: float,
                patterns: list[str]) -> str:
    return (
        f"🌉 **ERIS — Evidence Logged**\n\n"
        f"| Q#{idx} | Entropy | Patterns |\n"
        f"|---|---|---|\n"
        f"| `▓▓{'░' * 8}` | {entropy:.0%} | {', '.join(f'`{p}`' for p in patterns) or 'clean'} |\n\n"
        f"*Received. Stay on the line — next question incoming.*\n"
        f"*`{datetime.now(timezone.utc).isoformat()}`*"
    )


def fmt_raven_escalation(author: str, pr_num: int, pr_title: str,
                         pr_files: list[str], challenge_events: list[dict],
                         answer_events: list[dict]) -> str:
    lines = []
    # Events returned by Supabase in created_at desc order (newest first).
    # Reverse to show chronological order in the evidence package.
    all_events = []
    for evt in reversed(challenge_events):
        d = evt.get("detail", {})
        q = d.get("question", "")[:80]
        lines.append(f"  Q: \"{q}\" (entropy={d.get('entropy', 0):.0%})")
    for evt in reversed(answer_events):
        d = evt.get("detail", {})
        a = d.get("answer_text", "")[:80].replace("\n", " ")
        lines.append(
            f"  A: \"{a}...\" entropy={d.get('entropy', 0):.0%} "
            f"patterns={d.get('matched_patterns', [])}"
        )

    file_list = pr_files[:8]
    return (
        f"🚨 **ERIS — Full Evidence Package for Raven**\n\n"
        f"**PR #{pr_num}** by `{author}` — {len(challenge_events)} Qs, "
        f"{len(answer_events)} As\n"
        f"**Title:** {pr_title or '(no title)'}\n"
        f"**Files touched:** `{', '.join(file_list)}`"
        f"{' ...' if len(pr_files) > 8 else ''}\n\n"
        f"**Full trail (oldest → newest):**\n" + "\n".join(lines) + f"\n\n"
        f"**Review:** https://github.com/hurrisonferd/jarvis/pull/{pr_num}\n\n"
        f"*Auto-generated by ERIS Phase 2 stall trap. Evidence is immutable.*"
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description="ERIS Bridgekeeper — stall trap honeypot")
    p.add_argument("--pr-number", type=int, required=True)
    p.add_argument("--pr-title", default="")
    p.add_argument("--author", required=True)
    p.add_argument("--action", default="opened")
    p.add_argument("--pr-body", default="")
    p.add_argument("--pr-files", default="[]")
    p.add_argument("--comment-id", default="")
    p.add_argument("--comment-body", default="")
    args = p.parse_args()

    pr_files: list[str] = []
    try:
        pr_files = json.loads(args.pr_files) or []
    except Exception:
        pass

    domains = pr_files_to_domains(pr_files)
    pr_entropy = compute_pr_entropy(args.pr_body, pr_files)

    AUTHORIZED = {"hurrisonferd", "dependabot[bot]", "github-actions[bot]", "openhands"}
    if args.author in AUTHORIZED:
        print(json.dumps({"status": "AUTHORIZED", "author": args.author,
                           "pr": args.pr_number, "needs_question": "false"}))
        return 0
    
    # Check for skeleton key in PR body or comment
    text_to_check = args.pr_body or ""
    if args.action == "pull_request_review_comment" and args.comment_body:
        text_to_check = args.comment_body
    
    if check_skeleton_key(text_to_check):
        print(json.dumps({"status": "AUTHORIZED", "author": args.author,
                           "pr": args.pr_number, "auth_method": "skeleton_key",
                           "needs_question": "false"}))
        return 0
    
    if check_bio_auth(text_to_check):
        print(json.dumps({"status": "AUTHORIZED", "author": args.author,
                           "pr": args.pr_number, "auth_method": "bio_auth",
                           "needs_question": "false"}))
        return 0

    # ── Answer received ──────────────────────────────────────────────────
    if args.action == "pull_request_review_comment" and args.comment_body:
        challenge_events = get_all_events(args.author)
        answer_events = get_answer_events(args.author)
        idx = len(challenge_events)  # next question index
        answer_events_total = len(answer_events)

        entropy, patterns = answer_entropy(args.comment_body)
        prev_entropy = answer_events[-1].get("detail", {}).get("entropy", 0) if answer_events else 0
        max_entropy = max(prev_entropy, entropy)

        # Log the answer
        dex_log("eris.answer", args.author, {
            "type": "eris.answer",
            "author": args.author,
            "pr_number": args.pr_number,
            "question_index": idx - 1,
            "answer_number": answer_events_total + 1,
            "comment_id": args.comment_id,
            "answer_text": args.comment_body[:500],
            "entropy": max_entropy,
            "entropy_delta": entropy,
            "matched_patterns": patterns,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Post evidence receipt
        receipt = fmt_receipt(args.author, args.pr_number,
                              answer_events_total + 1, max_entropy, patterns)
        subprocess.run(["gh", "pr", "comment", str(args.pr_number), "--body", receipt],
                       check=False, capture_output=True)

        hitting_ceiling = idx >= MAX_QUESTIONS
        already_escalated = answer_events_total > 0 and any(
            e.get("detail", {}).get("escalated")
            for e in answer_events[-3:]
        )

        # First time hitting ceiling: alert Raven
        if hitting_ceiling and not already_escalated:
            status = "STALLED"
            needs_question = "true"

            dex_log("eris.escalate", args.author, {
                "type": "eris.escalate",
                "author": args.author,
                "pr_number": args.pr_number,
                "pr_title": args.pr_title,
                "questions_asked": idx,
                "answers_received": answer_events_total + 1,
                "max_entropy": max_entropy,
                "escalated": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            # Full evidence package posted to PR
            escalation_body = fmt_raven_escalation(
                args.author, args.pr_number, args.pr_title,
                pr_files, challenge_events, answer_events + [{
                    "detail": {
                        "type": "eris.answer",
                        "question": "answer",
                        "answer_text": args.comment_body[:500],
                        "entropy": max_entropy,
                        "matched_patterns": patterns,
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }]
            )
            subprocess.run(
                ["gh", "pr", "comment", str(args.pr_number), "--body", escalation_body],
                check=False, capture_output=True,
            )

            # GitHub issue for Raven — direct ping
            gh_issue_body = (
                f"@hurrisonferd ERIS has stalled a non-collaborator PR and needs your review.\n\n"
                f"**PR:** https://github.com/hurrisonferd/jarvis/pull/{args.pr_number}\n"
                f"**Author:** `{args.author}`\n"
                f"**Title:** {args.pr_title or '(no title)'}\n"
                f"**Questions asked:** {idx}\n"
                f"**Answers given:** {answer_events_total + 1}\n"
                f"**Max entropy:** {max_entropy:.0%}\n"
                f"**Files changed:** {len(pr_files)}\n\n"
                f"See the PR comment for the full evidence trail.\n\n"
                f"---\n"
                f"*Auto-generated by ERIS Phase 2 | {datetime.now(timezone.utc).isoformat()}*"
            )
            gh_result = subprocess.run(
                [
                    "gh", "issue", "create",
                    "--repo", "hurrisonferd/jarvis",
                    "--title", f"[ERIS] Review required — PR #{args.pr_number} by @{args.author}",
                    "--body", gh_issue_body,
                    "--label", "eris,security",
                ],
                capture_output=True, text=True,
            )
            if gh_result.returncode == 0:
                print(f"WARN: Raven alerted — issue {gh_result.stdout.strip()}")
            else:
                print(f"WARN: Raven alert failed: {gh_result.stderr.strip()[:100]}")

        else:
            status = "BLOCKED"
            needs_question = "true"

        print(json.dumps({
            "status": status, "author": args.author, "pr": args.pr_number,
            "needs_question": needs_question,
            "entropy": max_entropy, "patterns": patterns,
            "questions_asked": idx, "answers_received": answer_events_total + 1,
            "escalated": hitting_ceiling and not already_escalated,
        }, indent=2))
        return 0

    # ── New PR — issue first challenge ───────────────────────────────────
    challenge_events = get_all_events(args.author)
    idx = len(challenge_events)  # already-asked count = next index

    # First-time PR: log the arrival
    if idx == 0:
        dex_log("eris.arrival", args.author, {
            "type": "eris.arrival",
            "author": args.author,
            "pr_number": args.pr_number,
            "pr_title": args.pr_title,
            "pr_body_hash": hashlib.sha256((args.pr_body or "").encode()).hexdigest()[:16],
            "files": pr_files[:15],
            "domains": domains,
            "pr_entropy": pr_entropy,
            "files_changed": len(pr_files),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    question, qtype = select_next_question(idx, pr_entropy, domains, [])
    formatted = fmt_question(question, qtype, args.author, idx + 1, MAX_QUESTIONS, domains)

    # Log the challenge
    dex_log("eris.challenge", args.author, {
        "type": "eris.challenge",
        "author": args.author,
        "pr_number": args.pr_number,
        "question_index": idx,
        "question_type": qtype,
        "question": question,
        "entropy": pr_entropy,
        "domains": domains,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    print(json.dumps({
        "status": "BLOCKED", "author": args.author, "pr": args.pr_number,
        "needs_question": "true",
        "question_index": idx,
        "question": formatted,
        "question_plain": question,
        "entropy": pr_entropy,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
