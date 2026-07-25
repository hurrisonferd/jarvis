/**
 * MCP session lifecycle — AsyncLocalStorage for async-safe request context.
 *
 * Every inbound MCP call carries:
 *   X-Session-ID:   <id>     (optional; caller-provided conversation identifier)
 *   X-Companion:    <name>   (optional; defaults to 'Jarvis-G')
 *   X-Session-End:  <bool>   (optional; true = force close this session)
 *
 * Session key = X-Session-ID if present, else `${Date.now()}`.
 * The key is stable across calls within the inactivity window.
 *
 * Stored in Supabase mcp_sessions table. Session start/close/pulse handled by
 * stored procedures (mcp_session_open / mcp_session_close / mcp_session_pulse).
 *
 * Usage:
 *   const store = createSessionStore();
 *   await store.run(req.headers, async () => {
 *     // all tools called here can use currentSession()
 *     const s = currentSession();
 *   });
 */

import { AsyncLocalStorage } from "node:async_hooks";
import { SUPABASE_URL, SERVICE_KEY } from "./env.ts";
import { logExchange } from "./supabase.ts";

export interface SessionInfo {
  session_key: string;
  companion: string;
  started_at: string;
  exchanges: number;
  topics: string[];
}

/** In-memory map of active sessions — keyed by session_key.
 * Resets on edge-function cold start (acceptable: sessions are also in DB).
 * Max ~10k entries before eviction, which is fine for MCP usage.
 */
const _active = new Map<string, { key: string; companion: string; started_at: Date; exchanges: number; topics: Set<string> }>();

// ── AsyncLocalStorage ────────────────────────────────────────────────────────────

/** Async-safe request context store. Created once per edge-function instance.
 * Wraps async operations so session context propagates through all tool handlers. */
export const sessionStore = new AsyncLocalStorage<SessionInfo | null>();

export function setCurrentSession(s: SessionInfo | null): void {
  // No-op: context is managed by sessionStore.run()
}
export function currentSession(): SessionInfo | null {
  return sessionStore.getStore() ?? null;
}

// ── Key derivation ─────────────────────────────────────────────────────────────

/** Derive a stable session key from request headers. */
export function sessionKey(headers: Headers): string {
  const id = headers.get("X-Session-ID");
  if (id?.trim()) return id.trim();
  // Fall back to millisecond timestamp of first call — two calls in the same ms
  // get the same key, which is acceptable (they are effectively the same logical turn).
  return `${Date.now()}`;
}

/** Companion stream name, inferred from header or defaulted. */
export function sessionCompanion(headers: Headers): string {
  return headers.get("X-Companion")?.trim() ?? "Jarvis-G";
}

// ── Git head ───────────────────────────────────────────────────────────────────

/** Returns the current git SHA of the deployed edge function, or null on error.
 * Used to stamp the session with the state of code at session open. */
export async function gitHead(): Promise<string | null> {
  // Edge functions don't have a .git dir. The SHA is injected at deploy time
  // via an env var set by the CI pipeline (supabase functions deploy).
  return Deno.env.get("DEPLOY_SHA") ?? null;
}

// ── RPC helpers ────────────────────────────────────────────────────────────────

async function rpc<T = unknown>(fn: string, params: Record<string, unknown>): Promise<T> {
  const body = new URLSearchParams({ ...params }).toString();
  const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/${fn}`, {
    method: "POST",
    headers: {
      "authorization": `Bearer ${SERVICE_KEY}`,
      "apikey": SERVICE_KEY,
      "content-type": "application/x-www-form-urlencoded",
      "prefer": "return=minimal",
    },
    body,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`rpc/${fn} failed ${res.status}: ${detail.slice(0, 120)}`);
  }
  return (await res.json()) as T;
}

// ── Core API ───────────────────────────────────────────────────────────────────

/** Get or create a session. Idempotent — safe to call on every tool invocation.
 * Writes SL_SESSION_START + BIFROST.session_start on first call only. */
export async function getOrCreateSession(
  headers: Headers,
  toolName: string | null,
): Promise<SessionInfo> {
  const key = sessionKey(headers);
  const companion = sessionCompanion(headers);
  const isEnd = headers.get("X-Session-End")?.toLowerCase() === "true";

  if (isEnd) {
    await closeSession(key);
    return { session_key: key, companion, started_at: new Date().toISOString(), exchanges: 0, topics: [] };
  }

  // Check in-memory first (fast path)
  let s = _active.get(key);
  if (!s) {
    // Check DB
    const gh = await gitHead();
    try {
      await rpc("mcp_session_open", { p_session_key: key, p_companion: companion, p_git_head: gh ?? undefined });
    } catch (e) {
      console.error("mcp_session_open RPC failed:", String(e).slice(0, 120));
    }
    s = { key, companion, started_at: new Date(), exchanges: 0, topics: new Set() };
    _active.set(key, s);
  }

  // Pulse: update last_call + increment exchanges + infer topic
  if (toolName) {
    const topic = inferTopic(toolName);
    s.exchanges++;
    if (topic) s.topics.add(topic);
    try {
      await rpc("mcp_session_pulse", { p_session_key: key, p_tool_name: toolName });
    } catch (e) {
      // non-fatal
    }
  }

  return {
    session_key: key,
    companion,
    started_at: s.started_at.toISOString(),
    exchanges: s.exchanges,
    topics: [...s.topics],
  };
}

/** Run an async operation within a session context.
 * Sets up session (start or resume), runs `fn` with context active,
 * then clears context. The preferred entry point from buildServer.
 *
 * Usage:
 *   const store = createSessionStore();
 *   await store.run(req.headers, async () => {
 *     // all tools called here can use currentSession()
 *     const s = currentSession();
 *   });
 */
export async function withSession<T>(
  headers: Headers,
  toolName: string | null,
  fn: () => Promise<T>,
): Promise<T> {
  const key = sessionKey(headers);
  const companion = sessionCompanion(headers);
  const isEnd = headers.get("X-Session-End")?.toLowerCase() === "true";

  if (isEnd) {
    await closeSession(key);
    return sessionStore.run(null, fn);
  }

  // Get or create session
  let s = _active.get(key);
  if (!s) {
    const gh = await gitHead();
    try {
      await rpc("mcp_session_open", {
        p_session_key: key,
        p_companion: companion,
        p_git_head: gh ?? undefined,
      });
    } catch (e) {
      console.error("mcp_session_open:", String(e).slice(0, 120));
    }
    s = { key, companion, started_at: new Date(), exchanges: 0, topics: new Set() };
    _active.set(key, s);
  }

  // Pulse
  if (toolName) {
    const topic = inferTopic(toolName);
    s.exchanges++;
    if (topic) s.topics.add(topic);
    try {
      await rpc("mcp_session_pulse", { p_session_key: key, p_tool_name: toolName });
    } catch { /* non-fatal */ }
  }

  const info: SessionInfo = {
    session_key: key,
    companion,
    started_at: s.started_at.toISOString(),
    exchanges: s.exchanges,
    topics: [...s.topics],
  };

  return sessionStore.run(info, fn);
}

/** Close a session explicitly. Idempotent — safe to call on X-Session-End. */
export async function closeSession(
  key: string,
  brief?: string,
  alignment?: number,
  patches?: string[],
): Promise<void> {
  _active.delete(key);
  try {
    await rpc("mcp_session_close", {
      p_session_key: key,
      p_brief: brief ?? null,
      p_alignment: alignment ?? null,
      p_patches: patches ?? null,
    });
    await logExchange("mcp_session", `session_close: ${key}`);
  } catch (e) {
    console.error("mcp_session_close RPC failed:", String(e).slice(0, 120));
  }
}

/** Write a session-scoped exchange log entry. */
export async function logSessionExchange(
  headers: Headers,
  exchangeType: string,
  content: string,
): Promise<void> {
  const key = sessionKey(headers);
  await logExchange(`mcp:${exchangeType}`, `[${key.slice(0, 12)}] ${content}`);
}

/** Close all active sessions — call on graceful shutdown (not possible in edge,
 * but here for completeness). In practice, pg_cron closes stale sessions. */
export async function closeAllSessions(): Promise<void> {
  for (const key of _active.keys()) {
    await closeSession(key);
  }
}

// ── Topic inference ─────────────────────────────────────────────────────────────

const TOPIC_MAP: Record<string, string> = {
  jarvis_query: "reasoning",
  jarvis_recall: "memory",
  jarvis_suit_up: "identity",
  jarvis_now: "telemetry",
  jarvis_council: "governance",
  jarvis_jip_get: "jip",
  jarvis_jip_list: "jip",
  jarvis_db_query: "database",
  jarvis_db_list: "database",
  jarvis_resolve: "resolution",
};

function inferTopic(toolName: string): string {
  return TOPIC_MAP[toolName] ?? "tools";
}
