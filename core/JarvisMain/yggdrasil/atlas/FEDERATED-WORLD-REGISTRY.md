---
memory_tier: JLTM
grade: draft
status: expansion
authority: Raven
---

# Federated World Registry

## Purpose

Define how Yggdrasil, Jarvis Dictionary, JNL, LAL, and JMS govern a world whose truth is distributed across multiple repositories and branches.

This document is a draft archaeology and restoration artifact. It does not change canonical authority or relocate truth.

## Current accessible federation

| Repository | Visibility | Default branch | Indexed | Current role hypothesis | Branch count observed |
|---|---|---:|---:|---|---:|
| `hurrisonferd/jarvis` | public | `main` | yes | public canon, original architecture, observer-safe execution and release surface | 143 |
| `hurrisonferd/Jarvis-Private` | private | `main` | yes | private Grid truth, living continuity, restricted systems, research and internal execution | 104 |
| `hurrisonferd/MyUnityProject` | private | `main` | no | bounded Unity project node / execution world | 1 |
| `hurrisonferd/PachinkoBounce` | private | `main` | no | bounded project node | 1 |

Observed total: **249 branches across four repositories**.

## Federation law

> Repository boundaries define storage, visibility, deployment, and release domains. They do not define identity.

A persistent object's JNL identity must survive:

- movement between folders;
- movement between branches;
- promotion from branch to default branch;
- extraction into a dedicated repository;
- movement between public and private storage when authority permits;
- archival into an immutable historical surface.

JMS updates location mirrors. It does not mint a replacement identity merely because storage changed.

## Resolution chain across repositories

```text
JD explains
  -> JNL identifies
    -> Federated LAL locates repository + ref + path
      -> Yggdrasil resolves canonical truth
        -> execution systems act under visibility and authority constraints
```

A federated location record requires:

```yaml
jnl: ARCH-JFS-CORE-0001
repository: hurrisonferd/jarvis
ref: main
path: core/JarvisMain/yggdrasil/jfs/JFS-SPEC.md
visibility: public
authority: CANON
state: active
mirror_policy: pointer-only
```

No public registry may leak private content, private paths whose names are themselves restricted, credentials, or protected relationship data. Public mirrors may expose only approved identity and routing metadata.

## Repository object schema

Every governed repository should eventually possess:

| Field | Meaning |
|---|---|
| Repository JNL | stable identity of the repository node |
| Name | current GitHub repository name |
| Purpose | why this repository exists |
| Visibility | public / private |
| Authority | owner and promotion authority |
| Default branch | canonical integration ref |
| Truth boundary | what may be canonical here |
| Deployment boundary | what is released or executed from here |
| Upstream | repositories that provide inherited truth |
| Downstream | repositories or products that consume it |
| Lifecycle | active / incubation / archive / deprecated |
| Return path | how work returns to a governed integration surface |

## Branch object schema

A long-lived or consequential branch should possess:

| Field | Meaning |
|---|---|
| Branch identity | stable registry identity; branch name remains a Git ref, not the ontology |
| Repository | repository containing the ref |
| Base ref | integration lineage |
| Purpose | bounded job or world role |
| Owner / carrier | responsible ISO, agent, or human |
| State | active / review / merged / superseded / historical / disposable / unknown |
| Canonical authority | none until promoted unless explicitly designated |
| Unique lineage | commits not reachable from default branch |
| Return path | PR, merge, extraction, tag, archive, or verified deletion |
| Expiry / review trigger | condition requiring reassessment |

## Branch classes

```text
INTEGRATION
  default branches and protected release refs

ACTIVE WORKSPACE
  bounded long-form projects, migrations, research, ISO lanes

REVIEW
  branch has a PR or explicit promotion path

MERGED HISTORICAL
  work is reachable from the integration branch; preserve only when historical naming matters

UNMERGED UNIQUE
  contains unrecovered lineage; never delete without inspection

REPOSITORY SEED
  coherent subsystem suitable for extraction into its own repository

GENERATED TRANSIENT
  automated write, patch, backup, or agent branch with no remaining unique value

UNKNOWN
  insufficient evidence; fail closed
```

## Preliminary branch observations

### Public repository

The public repository has 143 observed branches. Major families include:

- `atom/*` — bounded ATOM construction lanes;
- `agent/*` — short-lived repair and integration work;
- `claude/*` — extensive original architecture and substrate development;
- `codex/*` — safety, cloud, MCP, and SAT work;
- `jarvis-write-*` and `jarvis-spell-*` — likely generated transient branches;
- named architecture branches such as `jd-semantic-pokedex-v2`, `pride-prosody-pipeline-v1`, and `musicos-portable-runtime-v1`;
- persistent surfaces such as `main`, `gh-pages`, and `gaming`.

### Private repository

The private repository has 104 observed branches. Major families include:

- numerous `backup-*` refs requiring deduplication and reachability checks;
- AYRE research and holographic JMS/JSL experiments;
- sovereign-memory, causal-governance, decision-manifold, workflow-resonance, and intent-decay research lanes;
- private MusicOS and automation work;
- worker branches and living-atlas navigation;
- `main` and `gh-pages` integration/deployment refs.

### Project repositories

`MyUnityProject` and `PachinkoBounce` currently expose only `main`. They are clean project boundaries but have not yet been semantically registered into the world map.

## Safety rules

1. No branch deletion by name pattern alone.
2. No deletion before comparing the branch tip and unique commits against its default branch.
3. Open PRs, protected refs, deployment refs, and active workspaces are presumed retained.
4. Backups are not presumed valuable merely because they are named backup; their unique reachability must be measured.
5. Generated branches are not presumed disposable until their commits are reachable elsewhere.
6. Repository extraction must preserve original commit lineage or create a receipt explaining any unavoidable loss.
7. Private truth never becomes public merely to simplify federation.
8. A branch becomes canon only through explicit promotion.

## Restoration sequence

1. Register repositories as world nodes.
2. Inventory every branch and associated PR.
3. Compare each branch with the repository default branch.
4. Classify unique commits and architectural value.
5. Identify repository-seed candidates.
6. Generate a non-destructive cleanup manifest.
7. Preserve important epochs with tags or archive refs.
8. Delete only after Raven approves a verified manifest and tooling supports branch-ref deletion.
9. Regenerate federated LAL mirrors.
10. Validate that all moved identities still resolve.

## Initial law

> Many repositories may hold the world. Only Yggdrasil may describe it as one world.
