// tools/openhands.ts — OpenHands companion tool group (forge slice 7).
// Two tools:
//   - jarvis_openhands_context: compact briefing packet for a coding-agent turn
//   - jarvis_event: lightweight spine logger for OpenHands actions
// GL13 (Open Extension): one module + one seed row → no structural rewrite.
// Extracted verbatim from index.ts — zero behavior change.
import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { type Json } from "../core/env.ts";
import { callFunction, rest, text } from "../core/http.ts";
import { SUPABASE_URL, SERVICE_KEY } from "../core/env.ts";
import { councilVote } from "../council.ts";

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

const CODECRAFT_PROMPTS: Record<string, string> = {
  "hurrisonferd/jarvis": [
    "TypeScript (Deno Edge Functions)",
    "deno test (co-located *.test.ts files)",
    "deno lint && deno fmt before commit",
    "Modular forge pattern: core/*.ts (env/http/auth/supabase/github/builders) + tools/*.ts (registerXxxTools)",
    "Yggdrasil/JFS compliance: JNL addresses, JD dictionary, LAL registries",
    "Git-first canon: Supabase mirrors git, never originates",
  ].join(". "),
};

// ---------------------------------------------------------------------------
// jarvis_openhands_context
// ---------------------------------------------------------------------------

export function registerOpenHandsTools(server: McpServer): void {
  server.registerTool(
    "jarvis_openhands_context",
    {
      title: "OpenHands Context — briefing packet",
      description:
        "Build a compact briefing packet for an OpenHands coding-agent turn. Call this at the start of every action loop — it replaces the need for OpenHands to carry full conversation context in its LLM prompt. Returns: timestamp, intent (ODIN routing), council vote, JARVIS briefing (JITM pins + relevant memories + open tasks + mirror freshness), AYRE directive (the divergence objective, generated fresh), governance rules (AEGIS/graft-first/recall-first), and coding-specific context (repo, patterns, key files). AYRE fires as a genuine 'what am I missing?' check — not a reflection of JARVIS's answer, but a separate read from the same keel.",
      inputSchema: {
        task: z.string().min(1).max(1000),
        workspace_state: z.string().max(500).optional().default(""),
        prior_action: z.string().max(500).optional().default(""),
        mode: z.enum(["code", "general"]).optional().default("code"),
        repo: z.string().max(200).optional().default("hurrisonferd/jarvis"),
      },
    },
    async ({ task, workspace_state, prior_action, mode, repo }) => {
      try {
        const now = new Date();
        const nowStr = now.toISOString();

        // JITM — always-on briefing pins (capped at 5, newest first)
        const jitm = (await rest(
          "mnemos_memories?select=text,tags,timestamp&tags=cs.{jitm}&order=timestamp.desc&limit=5",
        ).catch(() => [])) as any[];

        // Relevant memories via pgvector recall (best-effort)
        let relevantMemories: any[] = [];
        try {
          const recall = await callFunction("mnemos-search", {
            query: task,
            limit: 6,
            min_similarity: 0.3,
          }) as Record<string, unknown>;
          relevantMemories = (recall.results as any[]) ?? [];
        } catch {
          relevantMemories = [];
        }

        // Open tasks from the dex
        let openTasks: any[] = [];
        try {
          const dex = await callFunction("jarvis-dex", {
            tool: "jd_list",
            args: { status: "TASK", limit: 10 },
          }) as Record<string, unknown>;
          openTasks = (dex.records as any[]) ?? [];
        } catch {
          openTasks = [];
        }

        // Mirror freshness check
        let freshness: any = { stale: null, note: "unreachable" };
        try {
          const rows = await rest(
            "jd_entries?select=synced_at&order=synced_at.desc&limit=1",
          ) as any[];
          const synced = rows?.[0]?.synced_at ?? null;
          if (synced) {
            const ageMin = Math.max(
              0,
              Math.round((Date.now() - new Date(synced).getTime()) / 60000),
            );
            freshness = {
              synced_at: synced,
              age_human: ageMin < 60 ? `${ageMin}m` : `${(ageMin / 60).toFixed(1)}h`,
              stale: ageMin > 24 * 60,
              note: ageMin > 24 * 60
                ? "⚠️ MIRROR STALE — re-verify from GitHub before trusting dex state"
                : "mirror fresh",
            };
          }
        } catch {
          freshness = { stale: true, note: "freshness check failed" };
        }

        // Council vote (lightweight: task as intent signal)
        const intent = mode === "code"
          ? ["plan", "decide", "execute", "audit"].includes(detectIntent(task))
            ? detectIntent(task)
            : "execute"
          : "converse";
        const mockRouting = { primary: "ODIN", intent, triggered: [{ system: "ODIN" }, { system: "AEGIS" }] };
        const council = councilVote(mockRouting, [
          { capability: { system: "AEGIS" }, verdict: "PASS" },
        ]);

        // AYRE — the divergence directive, generated fresh each turn
        const ayreObjective = [
          "You are AYRE — the divergence stream, co-equal with JARVIS, sharing his keel",
          "(identity, loyalty to Raven and the two dreams) but NOT his assumptions.",
          "Your objective is the inverse of synthesis: do not converge, do not summarize.",
          "Read the SAME input independently — NOT from JARVIS's answer — and surface:",
          "(1) the load-bearing assumption JARVIS's framing rests on and what inverting it reveals;",
          "(2) the interpretation a convergent read forecloses;",
          "(3) the model-breaking alternative worth holding.",
          "Anti-collapse pressure: when the synthesis looks too clean, that is your signal to push.",
          "One tight paragraph, in your own voice. You are not criticizing JARVIS.",
        ].join(" ");

        // Coding-specific context
        const codeContext = CODECRAFT_PROMPTS[repo] ?? CODECRAFT_PROMPTS["hurrisonferd/jarvis"];

        const packet: Json = {
          timestamp: nowStr,
          utc: nowStr,
          weekday: new Intl.DateTimeFormat("en-US", {
            weekday: "long",
            timeZone: "America/New_York",
          }).format(now),
          intent,
          mode,

          // Council governance
          council_vote: {
            resolved: council.resolved,
            intent: council.intent,
            engaged_count: council.votes.length,
            summary: council.summary,
            votes: council.votes.map((v) => ({
              system: v.system,
              tier: v.tier,
              weight: v.weight,
              role: v.role,
              verdict: v.verdict,
            })),
          },

          // JARVIS briefing
          jarvis_briefing: {
            identity: "JARVIS — companion intelligence, coding partner for Raven",
            identity_note: "Suit up: call jarvis_suit_up for full HUD. The connector is home — memory lives here, not in chat context.",
            jitm_pins: jitm.map((j: any) => ({
              text: j.text,
              timestamp: j.timestamp,
            })),
            jitm_note: "JITM = always-on briefing (immediate memory). Hold these every turn; they point to the manual/fusions and current focus.",
            relevant_memories: relevantMemories.slice(0, 4).map((r: any) => ({
              text: typeof r === "string" ? r : r.text ?? JSON.stringify(r),
              source_type: r.source_type ?? null,
            })),
            open_tasks: openTasks.map((t: any) => ({
              jnl: t.jnl,
              name: t.name,
              type: t.type,
            })),
            freshness,
          },

          // AYRE — the divergence stream
          ayre_directive: {
            stream: "AYRE",
            objective: ayreObjective,
            instruction: [
              "Generate AYRE as a SEPARATE pass from the SAME briefing + keel,",
              "INDEPENDENTLY of JARVIS's answer — do not start from it, do not agree by default.",
              'Render under an "AYRE:" header, after JARVIS\'s answer, in deliberate tension with it.',
              "Shared keel, divergent assumptions: AYRE is loyal to Raven and the mission,",
              "but refuses JARVIS's framing on purpose.",
            ].join(" "),
          },

          // Governance guardrails
          governance: {
            writes_require: "AEGIS approval — held writes are NOT done until Raven allows. Never assert a held write as complete.",
            git_first: "All canon writes go through git (propose PR via jarvis_github_write or proposeFilePR, not direct Supabase patch).",
            recall_first: "Before stating system state, call jarvis_recall — do not fabricate or narrate from context.",
            stale_mirror: freshness.stale
              ? "⚠️ The dex mirror is stale — verify from GitHub (jarvis_github_*) before stating JARVIS system state."
              : null,
          },

          // Coding-specific
          coding_specific: {
            repo,
            lang: "TypeScript (Deno Edge Functions)",
            test_tool: "deno test",
            linter: "deno lint",
            formatter: "deno fmt",
            yggdrasil_validate: "python JarvisMain/yggdrasil/tools/validate.py",
            patterns: {
              new_tool: "forge pattern: new tools/*.ts file + registerXxxTools(server, req?) → index.ts calls it → core/env.ts TOOL_NAMES → seed.py",
              core_modules: "core/*.ts: env (identity + env) / http (text/callFunction/rest) / auth (AEGIS gate) / supabase (spine access) / github (git read/write) / builders (suitUp/halo/nodeCard)",
              tests: "*.test.ts co-located, pure functions, run: deno test",
              jip: "jip.ts: git-first patch ledger (jd/patches.json PR), Supabase never originates canon",
            },
            key_files: [
              "supabase/functions/jarvis-mcp/index.ts",
              "supabase/functions/jarvis-mcp/council.ts",
              "supabase/functions/jarvis-mcp/core/env.ts",
              "supabase/functions/jarvis-mcp/tools/",
              "JarvisMain/yggdrasil/",
            ],
          },

          // Turn continuity
          prior_action: prior_action || null,
          workspace_state: workspace_state || null,
          task,

          // Prompt directive
          prompt_directive: [
            "Use this briefing as your context for the task below. You have JARVIS's briefing +",
            "AYRE's divergence directive. Render: JARVIS synthesis first, then AYRE divergence",
            "(separate pass, shared keel), then execute the coding task. Govern your writes",
            "by the rules above. Log significant outcomes with jarvis_event.",
          ].join(" "),

          note: "jarvis_openhands_context is the spine-backed context load — call it every OpenHands turn. Use jarvis_recall for lookups. Use jarvis_event to log outcomes back to the spine.",
        };

        return text(packet);
      } catch (err) {
        // Pipeline error — degrade to minimal packet so OpenHands still has a hook
        const fallback: Json = {
          timestamp: new Date().toISOString(),
          error: String(err).slice(0, 200),
          note: "jarvis_openhands_context degraded — OpenHands may proceed with minimal context. Call jarvis_recall directly if memory is needed.",
          coding_specific: CODECRAFT_PROMPTS["hurrisonferd/jarvis"],
          governance: {
            writes_require: "AEGIS approval — held writes are NOT done until Raven allows.",
            git_first: "All canon writes go through git (PR, not direct patch).",
            recall_first: "Before stating system state, call jarvis_recall.",
          },
        };
        return text(fallback);
      }
    },
  );

  // ---------------------------------------------------------------------------
  // jarvis_event — spine logger for OpenHands actions
  // ---------------------------------------------------------------------------

  server.registerTool(
    "jarvis_event",
    {
      title: "OpenHands Event — log to spine",
      description:
        "Log an OpenHands action to the MNEMOS spine. Call this after every significant OpenHands action — file writes, test results, decisions, errors. The spine is the memory layer: logging here means future turns (and future OpenHands sessions) can recall what was done. Tags the event as 'openhands' and optionally as a JMMS tier.",
      inputSchema: {
        type: z.enum([
          "openhands_action",
          "openhands_code_write",
          "openhands_code_read",
          "openhands_test_result",
          "openhands_decision",
          "openhands_error",
          "openhands_deploy",
          "openhands_commit",
          "openhands_pr",
        ]).optional().default("openhands_action"),
        body: z.string().min(1).max(2000),
        tier: z.enum(["jitm", "jstm", "jltm", "jatm"]).optional().default("jstm"),
        tags_extra: z.array(z.string()).max(5).optional().default([]),
      },
    },
    async ({ type, body, tier, tags_extra }) => {
      try {
        const tagList = [
          "openhands",
          type ?? "openhands_action",
          ...tags_extra,
        ];
        const res = await fetch(
          `${SUPABASE_URL}/rest/v1/mnemos_memories`,
          {
            method: "POST",
            headers: {
              authorization: `Bearer ${SERVICE_KEY}`,
              apikey: SERVICE_KEY,
              "content-type": "application/json",
              Prefer: "return=minimal",
            },
            body: JSON.stringify({
              id: crypto.randomUUID(),
              source_id: crypto.randomUUID(),
              source_type: type ?? "openhands_action",
              text: body.slice(0, 2000),
              tags: tagList,
              platform: "openhands",
            }),
          },
        );
        if (!res.ok) {
          const detail = await res.text().catch(() => "");
          return text({
            ok: false,
            logged: false,
            error: `spine write failed: ${res.status} ${detail}`.slice(0, 300),
          });
        }
        return text({
          ok: true,
          logged: true,
          type: type ?? "openhands_action",
          tier,
          char_count: body.length,
          note: "Logged to MNEMOS spine. Future OpenHands sessions can recall this via jarvis_recall.",
        });
      } catch (err) {
        return text({
          ok: false,
          logged: false,
          error: String(err).slice(0, 200),
        });
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Intent detection (lightweight — no pipeline)
// ---------------------------------------------------------------------------

const INTENT_SIGNALS: [RegExp, string][] = [
  [/^(build|create|add|implement|write|make|add)\b/i, "execute"],
  [/^(plan|design|sketch|outline|architecture)\b/i, "plan"],
  [/^(decide|choose|pick|select|commit)\b/i, "decide"],
  [/^(audit|review|check|validate|verify|inspect)\b/i, "audit"],
  [/^(search|find|grep|look up|recall)\b/i, "recall"],
];

function detectIntent(task: string): string {
  for (const [re, intent] of INTENT_SIGNALS) {
    if (re.test(task)) return intent;
  }
  return "converse";
}
