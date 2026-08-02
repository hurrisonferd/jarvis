# BlackwallOS Public Compatibility Boundary

Status: PUBLIC-SAFE SCAFFOLD
Authority: Raven
Private canonical implementation: `hurrisonferd/Jarvis-Private`

## Purpose

This document defines what the public repository may expose about BlackwallOS without publishing private identity data, recovery material, security incidents, credentials, internal receipts, or operational attack-surface details.

## Public-safe surface

The public repository may contain:

- neutral decision enums: `ALLOW`, `LIMIT`, `CHALLENGE`, `QUARANTINE`, `DENY`, `ESCALATE`;
- generic event and evidence schemas;
- synthetic canary fixtures;
- defensive input-validation and replay-protection examples;
- public abuse-rate and contribution boundaries;
- nonfunctional decoy examples;
- documentation explaining owner-safe recovery and privacy principles.

## Private-only surface

The public repository must not contain:

- raw sovereign-data or biography corpora;
- real bio-auth questions or answers;
- recovery secrets, hashes, passkeys or factor records;
- private ERIS identity or memory records;
- exact production RLS findings before remediation;
- private Supabase table contents;
- credentials, token material or secret-derived values;
- live honeypot targets or tracing identifiers;
- operational incident evidence;
- privileged connector capability details that increase attackability.

## Public contract

Public Blackwall-compatible components must:

1. treat biographical knowledge as context, never a master password;
2. minimize collection and retention;
3. provide bounded challenge and appeal behavior;
4. distinguish public, familiar, trusted, private and sealed data;
5. never retaliate or probe third parties;
6. produce redacted receipts;
7. require explicit authority for consequential mutation;
8. remain reversible and testable.

## Relationship to private BlackwallOS

The public surface is a compatibility contract and learning surface. It is not the canonical policy engine, private corpus, incident archive or deployment configuration.

Cross-repository exports require an explicit `PUBLIC_SAFE` classification and evidence that no private data or operational secret is included.
