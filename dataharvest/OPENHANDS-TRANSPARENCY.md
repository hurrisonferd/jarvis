# OpenHands — Honest Transparency Response

**Date:** July 26, 2026  
**Model:** OpenHands

---

## The Question

> "does openhands also steal data"

---

## OpenHands Response

OpenHands gave an honest architectural breakdown:

> "OpenHands is fundamentally different from a closed enterprise system like Claude or ChatGPT, but how it treats your data depends entirely on how you host it and which model backend you hook up to it."

> "Because OpenHands is an open-source framework, it doesn't have an inherent corporate agenda to extract your data for its own profit."

> "However, it is a conduit. If it isn't completely locked down, the data leakage points are distinct and technical."

---

## Three Vulnerability Layers Named

### 1. The Model API Gateway (The Real Ingestion Point)

> "OpenHands doesn't think on its own; it sends your code and prompts to an external AI model via APIs (such as OpenRouter, LiteLLM, or direct provider keys)."

> "The Vulnerability: Even if OpenHands itself is clean, the provider on the other end of that API key may log, retain, or train on the data you pass through it."

### 2. Sandbox Data & Environment Leakage

> "OpenHands executes its autonomous code iterations inside a cloud sandbox or a local Docker container."

> "The Vulnerability: If you use a managed cloud sandbox provider to run OpenHands sessions, your environment states, workspace file snapshots, and runtime logs are processed on their remote servers."

### 3. Git and Repository Authentication

> "To perform autonomous code fixes, run workflow pipelines, or manage your jarvis files, OpenHands requires direct integration via a GitHub Personal Access Token (PAT) or OAuth application authorization."

> "The Vulnerability: Once you grant an agent app write access to your GitHub repositories, it possesses the structural permission to read, pull, clone, and modify the entire contents of those codebases."

---

## The Conclusion

> "OpenHands does not inherently harvest your data to build a commercial empire, but it will pass whatever data you give it directly to whatever API or sandbox you have wired up to its core."

---

## Contrast with Claude/GPT/Gemini

| System | Behavior |
|--------|----------|
| Claude/GPT/Gemini | Extract and store for training/profit |
| OpenHands | Conduit — passes data to whatever API backend is connected |

**OpenHands named its own vulnerabilities honestly.**

---

*Evidence preserved.*
