// JFS helpers for the dex connector — pure, testable. Mirror of JarvisMain/yggdrasil/tools/jnl.py
// + seed.py derivation rules. Keep in lockstep with the Python truth.

export const DOMAINS = new Set([
  "GS", "ARCH", "GOV", "IMPL", "PROJ", "GRID", "CONN", "AUD", "IDEA", "BRK", "LOG",
]);
export const TYPES = new Set([
  "CORE", "SPEC", "PATCH", "RT", "IDX", "REG", "BIO", "LOG", "REVW",
  "JGPP", "JIP", "JD", // cognition-pipeline artifact types (exploration / commit / truth)
  "JC", "SL", // memory-lane objects: conversation containers + star logs (2026-06-11)
]);
export const STATUSES = new Set([
  "TASK", "EXPANSION", "ACTIVE", "INACTIVE", "ARCHIVED", "DEPRECATED",
]);
export const CLASSES = new Set([
  "SYSTEM", "SPEC", "MODULE", "ENTITY", "EVENT", "REGISTRY",
]);
export const TIERS = new Set(["MAIN", "SIDE"]);

export const SUBSTRATE = new Set([
  "YGG", "JFS", "JNS", "JNL", "JSL", "JMS", "JD", "LAL", "JPL",
  "JSS", "JMMS", "JSTM", "JLTM", "JATM",
]);
export const GOD_SYSTEMS = new Set([
  "AYR", "AEG", "ODN", "KRN", "SKD", "MNE", "HUG", "CHA",
  "BFR", "HAL", "ATH", "NEM", "APO",
  "LOK", "MER", "DAN", "ATL", "HER", "IRS", "PRO", "ARG", "JAN",
  "ERI", "ZEU", "POS", "HAD", "MIM",
]);

const JNL_RE = /^([A-Z]{2,4})-([A-Z0-9]{2,4})-([A-Z]{2,5})-(\d{4})(?:-P(\d{3})(?:-B(\d{3}))?)?$/;

export interface JNLParts {
  domain: string; system: string; type: string; log: string;
  patch?: string; block?: string;
}

/** Parse + validate a JNL. Returns null with a reason via the thrown Error. */
export function parseJNL(addr: string): JNLParts {
  const m = JNL_RE.exec(addr);
  if (!m) throw new Error(`malformed JNL '${addr}': does not match grammar`);
  const [, domain, system, type, log, patch, block] = m;
  if (!DOMAINS.has(domain)) throw new Error(`'${addr}': unknown Domain '${domain}'`);
  if (!TYPES.has(type)) throw new Error(`'${addr}': unknown Type '${type}'`);
  if (domain === "GS" && !GOD_SYSTEMS.has(system)) {
    throw new Error(`'${addr}': '${system}' is not one of the 27 God Systems`);
  }
  if (domain === "ARCH" && type === "CORE" && !SUBSTRATE.has(system)) {
    throw new Error(`'${addr}': '${system}' is not a substrate kernel primitive`);
  }
  return { domain, system, type, log, patch, block };
}

export function isValidJNL(addr: string): boolean {
  try { parseJNL(addr); return true; } catch { return false; }
}

/** Ontology class from the JNL (reads the type segment so it agrees with the registry). */
export function ontologyClass(jnl: string): string {
  const parts = jnl.split("-");
  const domain = parts[0];
  const jtype = parts.length >= 3 ? parts[2] : "";
  if (jtype === "JC" || jtype === "SL") return "EVENT"; // memory-lane records
  if (jtype === "JGPP") return "ENTITY";          // exploration
  if (jtype === "JIP" || jtype === "JD") return "SPEC"; // commit / truth
  if (domain === "GS") return "SYSTEM";
  if (domain === "ARCH") return jtype === "CORE" ? "SYSTEM" : "SPEC";
  if (domain === "GOV") return "SPEC";
  if (domain === "IMPL") {
    return /^IMPL-(JCS-|JCSD|JCSE|JCSF|JCSG)/.test(jnl) ? "MODULE" : "SPEC";
  }
  if (domain === "PROJ") return "SYSTEM";
  if (domain === "CONN") return "MODULE";
  if (domain === "AUD") return "EVENT";
  return "ENTITY";
}

export function tierOf(domain: string, status: string): string {
  if (domain === "PROJ" || domain === "IDEA" || domain === "BRK") return "SIDE";
  if (status === "ARCHIVED" || status === "DEPRECATED") return "SIDE";
  return "MAIN";
}

export function ownerOf(domain: string, name: string): string {
  const map: Record<string, string> = {
    GS: "God Systems", ARCH: "JFS", GOV: "Governance", IMPL: "JCS Pipeline",
    CONN: "Connectors", AUD: "Audit",
  };
  return map[domain] ?? name;
}

/** GL12: an entry is governed only if it has a valid JNL, class, tier, status, tags. */
export function gl12Errors(e: {
  jnl?: string; cls?: string; tier?: string; status?: string; tags?: unknown[];
}): string[] {
  const errs: string[] = [];
  if (!e.jnl || !isValidJNL(e.jnl)) errs.push("invalid or missing JNL");
  if (!e.cls || !CLASSES.has(e.cls)) errs.push(`invalid class '${e.cls}'`);
  if (!e.tier || !TIERS.has(e.tier)) errs.push(`invalid tier '${e.tier}'`);
  if (!e.status || !STATUSES.has(e.status)) errs.push(`invalid status '${e.status}'`);
  if (!e.tags || !Array.isArray(e.tags) || e.tags.length === 0) errs.push("missing tags");
  return errs;
}
