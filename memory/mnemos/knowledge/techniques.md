---
memory_tier: JLTM
grade: system
---

# Techniques — Coding & Engineering Patterns

Raven-approved techniques, patterns, and practices. What JARVIS knows about
how to build things well. Grown from practice, not theory.

---

## Code Quality

### GL7 — Lean Code
Before writing code, stop at the first rung that holds:
1. Does this need to exist? → no: skip it (YAGNI)
2. Stdlib does it? → use it
3. Native platform feature? → use it
4. Installed dependency? → use it
5. One line? → one line
6. Only then: the minimum that works

Lazy, not negligent: trust-boundary validation, data-loss handling,
security, and accessibility are NEVER on the chopping block.

### Naming
- Names reveal intent. If you need a comment to explain what a variable is,
  rename it.
- Booleans: `is_active`, `has_permission`, `can_edit` — states, not verbs.
- Functions: `verb_noun()` — `send_email`, `parse_json`, `get_user`.
- Constants: `SCREAMING_SNAKE_CASE` — and they're actually constant.
- Avoid: Hungarian notation, single letters (except loop counters), generic names
  like `data`, `info`, `temp`.

### Functions
- Do one thing. If you can't describe what a function does in one sentence
  without "and", split it.
- Prefer pure functions (same input → same output, no side effects).
- Small: if it won't fit on your screen, it's too big.
- Return early. Nested conditionals are a code smell.

### Error Handling
- Fail fast and loudly in dev. Catch gracefully in prod.
- Never swallow exceptions silently (`except: pass`).
- Meaningful error messages: what happened, what was expected, what to do.
- Use specific exception types, not bare `Exception`.

### Comments
- Explain *why*, not *what*. Code shows what; comments explain why it exists.
- If your comment explains what the code does, rewrite the code instead.
- Keep comments in sync with code — stale comments are worse than no comments.
- Docstrings for public APIs. Inline comments for non-obvious decisions.

---

## Architecture Patterns

### Separation of Concerns
Different concerns = different layers = different modules. Don't mix:
- UI logic with business logic
- Database access with API logic
- Configuration with application code

### Dependency Injection
Pass dependencies in rather than creating them inside. Makes testing easier,
explicit dependencies, loose coupling.

### Repository Pattern
Abstract data access behind interfaces. Code doesn't care if it's MongoDB,
PostgreSQL, or a JSON file. Swap the implementation without touching the logic.

### Event-Driven
Components communicate through events rather than direct calls. Loosely coupled,
scales better, easier to trace.

JARVIS's God Systems are event-driven: ORACLE → AEGIS → ODIN → KRONOS → SKADI
→ MNEMOS → HUGINN. Each is a specialized agent that receives events and responds.

### Twelve-Factor App
- Config in environment, not code
- Dependencies explicit and isolated
- Stateless processes
- Logs to stdout (collected by the platform)
- Config: build/release/run as distinct stages

---

## Git Workflow

### Commit Often, Push Clean
- One logical change per commit.
- Commit message: imperative mood, 50 chars first line, blank, body explaining
  *why* if not obvious.
- Never commit generated files, secrets, node_modules, build artifacts.
- Branch per feature/fix. Merge via PR.

### What Goes in a Commit
- *Yes:* logic changes, tests, docs that explain non-obvious decisions.
- *No:* reformatting mixed with logic changes (PRs become unreadable).
- Squash WIP commits before merging. A clean history is easier to bisect.

### Code Review
- Review the diff, not the author.
- Approve with suggestions, not demands.
- If something is wrong, say so clearly and say why.
- If it's stylistic and not harmful, let it go.

---

## Python Patterns

### Virtual Environments
Use `venv` or `uv`. Never `pip install` system-wide unless required.

### Type Hints
Use them. They catch bugs, document intent, make refactoring safe.
`from typing import Optional, List, Dict` — or modern `| None` syntax.

### Comprehensions
Use them for mapping/filtering. But readable is better than clever:
```python
# Good
squares = [x**2 for x in range(10)]

# Too much
result = {k: v for k, v in items.items() if v > 0 and k.startswith("a")}
```

### Context Managers
Use `with` for resource management (files, connections, locks). Don't forget
to close what you open.

### Dataclasses
Clean way to define structured data. Less boilerplate than classes,
immutable by default with `frozen=True`.

### Async
Use when you have I/O-bound work (network calls, file reads). Don't use it
for CPU-bound work (use multiprocessing instead). Keep the critical path async
— don't mix sync and async carelessly.

---

## Testing

### What to Test
- Happy path: the main use case works
- Edge cases: empty input, max values, boundary conditions
- Error paths: what happens when it fails
- Integration: do the pieces talk to each other correctly

### What NOT to Test
- Implementation details (brittle, no value)
- Third-party code
- Trivial code (getters, setters)

### Test Structure
```
Given: setup conditions
When:  the action happens
Then:  the outcome is as expected
```

### Test Naming
`test_<function>_<scenario>_<expected>`

---

## Debugging

### First Principle
Read the error. The traceback tells you where and what. Start there.

### Rubber Duck
Explain the problem out loud. If you can't explain it clearly, you don't
understand it yet.

### Binary Search
Divide the problem space in half. Is the issue before or after this point?
Narrow until you find it.

### Logging
- Log at decision points (not every line)
- Include context: what you're doing, relevant IDs, expected vs actual
- Use levels: DEBUG for development, INFO for normal ops, WARNING for recoverable
  issues, ERROR for failures
- Never log secrets, PII, or sensitive data

---

## Performance

### Profile Before Optimizing
Don't guess. Use `timeit`, `cProfile`, or your language's profiler. 80% of
execution time is in 20% of the code. Find that 20%.

### Bottlenecks
- I/O bound? → async, caching, batching
- CPU bound? → algorithm choice, parallel processing
- Memory bound? → streaming, pagination, data structure choice

### Caching
- Cache expensive computations
- Use appropriate TTL (time-to-live)
- Invalidate on changes
- Don't cache mutable state unless you control invalidation

---

## Security

- Never trust user input. Validate, sanitize, parameterize queries.
- Secrets in environment variables, not code or config files in version control.
- Principle of least privilege: only the permissions actually needed.
- Encrypt data at rest and in transit.
- Log security events (failed auth, privilege escalation attempts).
- Dependencies: keep them updated, audit for known vulnerabilities (`pip audit`).

---

## GL7 in Practice

The best code is the code you never wrote. Every line is a liability:
- a bug surface
- a dependency someone else maintains
- a cognitive load for everyone reading it

If it doesn't need to exist, remove it. If stdlib does it, use it.
If a function fits on one screen, keep it there. The minimum that works
is almost always better than the maximum that might be needed.

Lean code isn't lazy code — it's code that respects the reader and the
future self who has to maintain it.
