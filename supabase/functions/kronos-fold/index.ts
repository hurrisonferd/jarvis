import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// KRONOS-triggered fold automation (Raven-directed 2026-06-24).
// JSTM → JHTM: memories older than 14 days compress into a digest receipt.
// JC → SL: session containers compress into star-log digests.
// Runs on a cron schedule via GitHub Actions; can also be triggered manually.
// One-way promotion: JSTM → JHTM → JLTM. Never demoted.
// IMPL-JMMS-0001: fold only non-session memories, system-grade by default,
// carry new JMMS columns (jstm_sub, temperature, activation_score) on fold.

const SB_URL  = Deno.env.get('SUPABASE_URL') ?? '';
const SB_KEY  = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '';
const DAYS    = parseInt(Deno.env.get('FOLD_DAYS') ?? '14', 10);
const CUTOFF  = new Date(Date.now() - DAYS * 86_400_000).toISOString();

interface FoldResult { table: string; promoted: number; errors: string[] }
interface JcRow { id: string; jnl: string; alias: string; session_date: string; subject: string; summary: string; events: string; decisions: string; keystones: string }
interface MemRow  { id: string; text: string; tags: string[]; source: string }

// ── compress ──────────────────────────────────────────────────────────────────
function compressEvents(events: unknown[]): string {
  if (!Array.isArray(events) || !events.length) return "";
  return events.slice(0, 10).map((e: any) => {
    const ts  = e?.timestamp ?? e?.ts ?? "";
    const role = e?.role ?? e?.author ?? "";
    const text = (e?.text ?? e?.content ?? JSON.stringify(e)).slice(0, 200);
    return `[${ts.slice(0, 16)} ${role}] ${text}`;
  }).join("\n");
}

// ── fold jc_objects: JSTM → JHTM, write SL ───────────────────────────────────
// IMPL-JMMS-0001: exclude session-scoped JCs; session-scoped memories die, not fold.
async function foldJcObjects(sb: ReturnType<typeof createClient>, grade?: string): Promise<FoldResult> {
  const result: FoldResult = { table: "jc_objects", promoted: 0, errors: [] };

  // IMPL-JMMS-0001: fold non-session JCs only; filter by grade if provided.
  let q = sb
    .from("jc_objects")
    .select("id, jnl, alias, session_date, subject, summary, events, decisions, keystones, memory_scope, grade")
    .eq("memory_tier", "jstm")
    .neq("memory_scope", "session")
    .lt("session_date", CUTOFF)
    .limit(50);
  if (grade) q = q.eq("grade", grade);
  else q = q.eq("grade", "system");
  const { data, error: fetchErr } = await q;

  if (fetchErr) { result.errors.push(fetchErr.message); return result; }
  if (!data?.length) return result;

  for (const jc of data as any[]) {
    const digest = [
      `# Star-Log — ${jc.alias ?? jc.jnl}`,
      `**Session:** ${jc.session_date}`,
      `**Subject:** ${jc.subject ?? ""}`,
      `**Summary:** ${jc.summary ?? ""}`,
      `**Decisions:** ${jc.decisions ?? ""}`,
      `**Keystones:** ${jc.keystones ?? ""}`,
      `**Events (compressed):**\n${compressEvents(JSON.parse(jc.events ?? "[]"))}`,
      ``,
      `*Folded from JC ${jc.jnl} · ${CUTOFF} · kronos-fold*`,
      `*IMPL-JMMS-0001: scope=${jc.memory_scope ?? "?"} grade=${jc.grade ?? "?"}*`,
    ].join("\n");

    const { error: slErr } = await sb.from("sl_objects").insert({
      jnl:      jc.jnl   ? `${jc.jnl}-SL`  : undefined,
      alias:    jc.alias ? `${jc.alias}-SL` : undefined,
      session_date: jc.session_date,
      digest,
      events: JSON.stringify({ folded_from: jc.jnl, folded_at: new Date().toISOString() }),
      memory_tier: "jhtm",
      jss_status:  "ACTIVE",
      status:      "folded",
      // IMPL-JMMS-0001: carry JMMS dimensions to SL
      memory_scope: jc.memory_scope ?? "project",
      grade: jc.grade ?? "system",
      temperature: "cool",
      activation_score: 0,
    });
    if (slErr) { result.errors.push(`SL insert: ${slErr.message}`); continue; }

    const { error: updErr } = await sb
      .from("jc_objects")
      .update({ memory_tier: "jhtm", jss_status: "ARCHIVED", status: "folded" })
      .eq("id", jc.id);
    if (updErr) { result.errors.push(`JC update: ${updErr.message}`); continue; }

    result.promoted++;
  }
  return result;
}

// ── fold mnemos_memories: JSTM → JHTM ───────────────────────────────────────
// IMPL-JMMS-0001: session-scoped memories die without folding; fold only system-grade
// (or whatever grade is passed). Carry JMMS dimensions on fold.
async function foldMnemosMemories(sb: ReturnType<typeof createClient>, grade?: string): Promise<FoldResult> {
  const result: FoldResult = { table: "mnemos_memories", promoted: 0, errors: [] };

  // IMPL-JMMS-0001: exclude session-scoped memories — they die, not fold.
  // Filter by grade (default system) so KRONOS doesn't fold personal memories.
  let q = sb
    .from("mnemos_memories")
    .select("id, text, tags, source, memory_scope, grade")
    .eq("memory_tier", "jstm")
    .neq("memory_scope", "session")
    .lt("created_at", CUTOFF)
    .limit(50);
  if (grade) q = q.eq("grade", grade);
  else q = q.eq("grade", "system"); // fold system by default; pass grade param to fold personal
  const { data, error: fetchErr } = await q;

  if (fetchErr) { result.errors.push(fetchErr.message); return result; }
  if (!data?.length) return result;

  for (const mem of data as MemRow[]) {
    const tags = mem.tags ?? [];
    const receiptTag = `fold:${new Date().toISOString().slice(0, 10)}:jstm→jhtm`;
    const foldedTags = [...new Set([
      ...tags.filter((t: string) => !t.startsWith("jitm") && !t.startsWith("jstm")),
      receiptTag,
    ])];
    // IMPL-JMMS-0001: carry JMMS dimensions on fold — reset jstm_sub, set temp cool, zero activation
    const receipt = `[FOLD RECEIPT ${new Date().toISOString()}] JSTM→JHTM | scope: ${(mem as any).memory_scope ?? "?"} | grade: ${(mem as any).grade ?? "?"} | source: ${mem.source ?? "?"} | chars: ${(mem.text ?? "").length}`;

    const { error: updErr } = await sb
      .from("mnemos_memories")
      .update({
        memory_tier: "jhtm",
        tags: foldedTags,
        text: mem.text + "\n\n---\n" + receipt,
        // IMPL-JMMS-0001: reset JMMS dimensions on fold
        jstm_sub: null,
        temperature: "cool",
        activation_score: 0,
      })
      .eq("id", mem.id);
    if (updErr) { result.errors.push(`mnemos update: ${updErr.message}`); continue; }
    result.promoted++;
  }
  return result;
}

// ── handler ───────────────────────────────────────────────────────────────────
Deno.serve(async (req: Request) => {
  const url     = new URL(req.url);
  const dryRun  = url.searchParams.get("dry") === "1";
  // IMPL-JMMS-0001: grade param lets KRONOS fold personal memories too (default: system)
  const foldGrade = url.searchParams.get("grade") === "personal" ? "personal" : undefined;

  // KRONOS-gated: only accept cron trigger or explicit dry run
  const auth      = req.headers.get("x-cron-secret") ?? "";
  const cronSecret = Deno.env.get("CRON_SECRET") ?? "";
  if (req.method === "POST" && auth !== cronSecret && !dryRun) {
    return new Response(JSON.stringify({ ok: false, error: "unauthorized" }), { status: 401 });
  }

  const sb = createClient(SB_URL, SB_KEY);
  const [jcResult, memResult] = await Promise.all([
    foldJcObjects(sb, foldGrade),
    foldMnemosMemories(sb, foldGrade),
  ]);

  const results = [jcResult, memResult];
  const total   = results.reduce((s, r) => s + r.promoted, 0);
  const errors  = results.flatMap(r => r.errors);

  if (dryRun) {
    return new Response(JSON.stringify({
      ok: true, dry: true, cutoff: CUTOFF, days: DAYS,
      fold_grade: foldGrade ?? "system",
      // IMPL-JMMS-0001: note session memories are excluded from fold target
      fold_scope_note: "memory_scope=session memories are excluded (they die, not fold)",
      ...Object.fromEntries(results.map(r => [r.table, { promoteable: r.promoted, errors: r.errors }])),
    }));
  }

  // Emit fold event to dex_events (P5: closure by proof)
  await sb.from("dex_events").insert({
    type: "kronos.fold",
    intent: "kronos.jstm_fold",
    payload: { cutoff: CUTOFF, days: DAYS, results, fold_grade: foldGrade ?? "system" },
    source: "kronos-fold",
  }).catch(() => {});

  return new Response(JSON.stringify({
    ok: true, cutoff: CUTOFF, days: DAYS, total, results, errors,
    fold_grade: foldGrade ?? "system",
    fold_scope_note: "memory_scope=session memories excluded (they die, not fold)",
  }));
});
