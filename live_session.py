#!/usr/bin/env python3
"""Raven Zero live session fallback.

Raven Zero is the quota-free floor for JARVIS-style interaction:
local capsule retrieval, deterministic command handling, approved scripts,
and optional local Ollama generation when explicitly configured.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


MAX_FILE_BYTES = 250_000
MAX_SNIPPETS = 6
SNIPPET_RADIUS = 260


SENSITIVE_PARTS = {
    ".env",
    ".git",
    "node_modules",
    "dist",
    "__pycache__",
    ".venv",
    "Jarvis-Private",
    "Jarvis-Private-work",
    "_work_private_repair",
    "_work_public_main",
}

SENSITIVE_NEEDLES = (
    "secret",
    "token",
    "password",
    "private_key",
    "service_role",
    "api_key",
    "sk-",
)


@dataclass(frozen=True)
class ScriptSpec:
    """Approved local script command."""

    description: str
    command: tuple[str, ...]


@dataclass
class RavenZeroConfig:
    repo_root: Path
    capsule_roots: tuple[Path, ...] = field(default_factory=tuple)
    approved_scripts: dict[str, ScriptSpec] = field(default_factory=dict)
    ollama_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = ""

    @classmethod
    def from_repo(cls, repo_root: Path) -> "RavenZeroConfig":
        repo_root = repo_root.resolve()
        return cls(
            repo_root=repo_root,
            capsule_roots=(
                repo_root / "BarberHistory",
                repo_root / "JarvisMain" / "Manual",
                repo_root / "JarvisMain" / "Architecture" / "specs",
                repo_root / "intake" / "recycle",
                repo_root / "README.md",
                repo_root / "CLAUDE.md",
            ),
            approved_scripts={
                "heartbeat-once": ScriptSpec(
                    "Observe repo/intake heartbeat once; writes only local heartbeat state.",
                    (sys.executable, "operations/scripts/jarvis_heartbeat.py", "--once"),
                ),
                "npm-validate": ScriptSpec(
                    "Run TypeScript build plus offline diagnostics.",
                    ("npm", "run", "validate"),
                ),
            },
            ollama_model=os.environ.get("RAVEN_ZERO_OLLAMA_MODEL", "").strip(),
            ollama_url=os.environ.get(
                "RAVEN_ZERO_OLLAMA_URL", "http://localhost:11434/api/generate"
            ).strip(),
        )


class RavenZeroEngine:
    """Deterministic local fallback backend for live sessions."""

    name = "Raven Zero"

    def __init__(self, config: RavenZeroConfig):
        self.config = config

    def respond(self, user_text: str) -> str:
        text = user_text.strip()
        lowered = text.lower()
        if not text:
            return "Raven Zero is online. Say `help` for local commands."

        if lowered in {"help", "/help", "?"}:
            return self.help_text()
        if lowered in {"status", "/status", "raven zero status"}:
            return self.status()
        if lowered in {"scripts", "/scripts", "approved scripts"}:
            return self.list_scripts()
        if lowered.startswith(("search ", "/search ")):
            return self.search(text.split(" ", 1)[1].strip())
        if lowered.startswith(("read ", "/read ")):
            return self.read_file(text.split(" ", 1)[1].strip())
        if lowered.startswith(("run ", "/run ")):
            return self.run_script(text.split(" ", 1)[1].strip())

        snippets = self.retrieve(text)
        if self.config.ollama_model and snippets:
            generated = self.try_ollama(text, snippets)
            if generated:
                return generated
        return self.extractive_answer(text, snippets)

    def help_text(self) -> str:
        return textwrap.dedent(
            """\
            Raven Zero commands:
              status                 Show local fallback status.
              search <query>          Search local capsule files.
              read <path>             Read a safe repo-relative file.
              scripts                 List approved local scripts.
              run <script-id>         Run one approved script.

            Natural questions use grounded extractive retrieval first.
            Set RAVEN_ZERO_OLLAMA_MODEL to enable optional local Ollama synthesis.
            """
        ).strip()

    def status(self) -> str:
        roots = [self._display_path(path) for path in self.config.capsule_roots if path.exists()]
        model = self.config.ollama_model or "disabled"
        return "\n".join(
            [
                "Raven Zero: ONLINE",
                "Mode: offline deterministic fallback",
                f"Repo: {self.config.repo_root}",
                f"Capsule roots: {len(roots)} available",
                f"Ollama model: {model}",
                f"Approved scripts: {len(self.config.approved_scripts)}",
            ]
        )

    def list_scripts(self) -> str:
        lines = ["Approved scripts:"]
        for script_id, spec in sorted(self.config.approved_scripts.items()):
            lines.append(f"- {script_id}: {spec.description}")
        return "\n".join(lines)

    def search(self, query: str) -> str:
        snippets = self.retrieve(query)
        if not snippets:
            return f"No grounded Raven Zero hits for: {query}"
        return self._format_snippets(snippets)

    def read_file(self, requested: str) -> str:
        path = self._resolve_repo_path(requested)
        if not path:
            return "Read denied: path must stay inside the repo."
        if self._is_sensitive(path):
            return "Read denied: sensitive or ignored path."
        if not path.is_file():
            return "Read failed: file not found."
        if path.stat().st_size > MAX_FILE_BYTES:
            return f"Read denied: file is larger than {MAX_FILE_BYTES} bytes."
        return path.read_text(encoding="utf-8", errors="replace")

    def run_script(self, script_id: str) -> str:
        spec = self.config.approved_scripts.get(script_id)
        if not spec:
            return f"Run denied: `{script_id}` is not in the approved script list."
        try:
            proc = subprocess.run(
                spec.command,
                cwd=self.config.repo_root,
                text=True,
                capture_output=True,
                timeout=120,
                check=False,
            )
        except FileNotFoundError as exc:
            return f"Run failed: command not found: {exc}"
        except subprocess.TimeoutExpired:
            return "Run stopped: approved script exceeded 120 seconds."

        output = (proc.stdout + proc.stderr).strip()
        if len(output) > 4000:
            output = output[:4000] + "\n...[truncated]"
        return f"Script `{script_id}` exited {proc.returncode}.\n{output or '(no output)'}"

    def retrieve(self, query: str) -> list[tuple[Path, str]]:
        terms = self._terms(query)
        if not terms:
            return []
        hits: list[tuple[int, Path, str]] = []
        for path in self._iter_capsule_files():
            if self._is_sensitive(path) or path.stat().st_size > MAX_FILE_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            lowered = text.lower()
            score = sum(lowered.count(term) for term in terms)
            name_score = sum(path.name.lower().count(term) for term in terms)
            score += name_score * 3
            if score <= 0:
                continue
            snippet = self._snippet(text, terms)
            hits.append((score, path, snippet))
        hits.sort(key=lambda item: item[0], reverse=True)
        return [(path, snippet) for _, path, snippet in hits[:MAX_SNIPPETS]]

    def extractive_answer(self, query: str, snippets: list[tuple[Path, str]]) -> str:
        if not snippets:
            return (
                "Raven Zero found no local capsule match. "
                "I can still run `search <query>`, `status`, or `scripts`."
            )
        return "\n".join(
            [
                "Raven Zero grounded answer:",
                f"Query: {query}",
                "",
                self._format_snippets(snippets),
                "",
                "No paid model was used. This is retrieval, not fluent synthesis.",
            ]
        )

    def try_ollama(self, query: str, snippets: list[tuple[Path, str]]) -> str:
        context = "\n\n".join(
            f"[{self._display_path(path)}]\n{snippet}" for path, snippet in snippets
        )
        prompt = (
            "You are Raven Zero, an offline JARVIS fallback. Answer only from the "
            "provided local context. If the context does not answer, say so.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        )
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        try:
            request = urllib.request.Request(
                self.config.ollama_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError):
            return ""
        answer = str(data.get("response", "")).strip()
        if not answer:
            return ""
        return f"Raven Zero + local Ollama ({self.config.ollama_model}):\n{answer}"

    def _iter_capsule_files(self) -> Iterable[Path]:
        for root in self.config.capsule_roots:
            if not root.exists():
                continue
            if root.is_file():
                yield root
                continue
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json", ".yaml", ".yml"}:
                    yield path

    def _resolve_repo_path(self, requested: str) -> Path | None:
        path = (self.config.repo_root / requested).resolve()
        try:
            path.relative_to(self.config.repo_root)
        except ValueError:
            return None
        return path

    def _is_sensitive(self, path: Path) -> bool:
        parts = set(path.parts)
        if parts & SENSITIVE_PARTS:
            return True
        lowered = str(path).lower()
        return any(needle in lowered for needle in SENSITIVE_NEEDLES)

    def _terms(self, query: str) -> list[str]:
        cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in query)
        return [term for term in cleaned.split() if len(term) >= 3][:8]

    def _snippet(self, text: str, terms: list[str]) -> str:
        lowered = text.lower()
        positions = [lowered.find(term) for term in terms if lowered.find(term) >= 0]
        if not positions:
            return text[: SNIPPET_RADIUS * 2].strip()
        center = min(positions)
        start = max(0, center - SNIPPET_RADIUS)
        end = min(len(text), center + SNIPPET_RADIUS)
        return text[start:end].strip().replace("\r\n", "\n")

    def _format_snippets(self, snippets: list[tuple[Path, str]]) -> str:
        blocks = []
        for path, snippet in snippets:
            blocks.append(f"Source: {self._display_path(path)}\n{snippet}")
        return "\n\n---\n\n".join(blocks)

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.config.repo_root))
        except ValueError:
            return str(path)


class LiveSession:
    """Live session wrapper whose default backend is Raven Zero."""

    def __init__(self, backend: RavenZeroEngine | None = None, repo_root: Path | None = None):
        root = repo_root or Path(__file__).resolve().parent
        self.backend = backend or RavenZeroEngine(RavenZeroConfig.from_repo(root))

    def ask(self, user_text: str) -> str:
        return self.backend.respond(user_text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Raven Zero live session fallback.")
    parser.add_argument("prompt", nargs="*", help="Optional one-shot prompt.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()

    session = LiveSession(repo_root=Path(args.repo_root))
    if args.prompt:
        print(session.ask(" ".join(args.prompt)))
        return 0

    print("Raven Zero online. Type `help` or Ctrl+C to exit.")
    while True:
        try:
            user_text = input("Raven> ")
        except (EOFError, KeyboardInterrupt):
            print("\nRaven Zero signing off.")
            return 0
        print(session.ask(user_text))


if __name__ == "__main__":
    raise SystemExit(main())
