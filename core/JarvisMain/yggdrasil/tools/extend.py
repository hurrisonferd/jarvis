"""extend — add a JNL grammar token (a Domain or a Type) in lockstep, one command.

The Law of Open Extension (GL13, proposed) in tool form. Domains and Types live in TWO
runtimes — jnl.py (the Python validator) and jarvis-dex/jfs.ts (the connector) — and
validate.py fails the build if they drift. Editing both by hand is the friction GL13 names a
defect. This writes both at once, idempotently, then tells you to reseed + validate.

(Systems under an existing domain need NO token — parse() only restricts GS and ARCH-*-CORE,
so a new system like IMPL-FOO-SPEC-0001 already validates. Only Domains/Types gate here.)

Usage:
  python core/JarvisMain/yggdrasil/tools/extend.py --check                 # report lockstep status
  python core/JarvisMain/yggdrasil/tools/extend.py --add-domain MUSIC      # add a Domain to both files
  python core/JarvisMain/yggdrasil/tools/extend.py --add-type LENS         # add a Type to both files
  python core/JarvisMain/yggdrasil/tools/extend.py --add-domain X --dry-run # show edits, write nothing

After an add: run seed.py then validate.py (the tool reminds you). A new domain usually wants an
index root too (see the orphan-lens pattern: mint <DOMAIN>-IDX-REG-0001 in seed.py).
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JNL_PY = ROOT / "JarvisMain" / "yggdrasil" / "tools" / "jnl.py"
JFS_TS = ROOT / "supabase" / "functions" / "jarvis-dex" / "jfs.ts"

# token grammar from the JNL regex segments: Domain [A-Z]{2,4}, Type [A-Z]{2,5}.
GRAMMAR = {"domain": (r"^[A-Z]{2,4}$", "DOMAINS"), "type": (r"^[A-Z]{2,5}$", "TYPES")}


def _py_set(text: str, name: str) -> set[str]:
    m = re.search(rf"{name} = \{{(.*?)\}}", text, re.DOTALL)
    return set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()


def _ts_set(text: str, name: str) -> set[str]:
    m = re.search(rf"export const {name} = new Set\(\[(.*?)\]\)", text, re.DOTALL)
    return set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()


def check() -> int:
    py, ts = JNL_PY.read_text(), JFS_TS.read_text()
    ok = True
    for name in ("DOMAINS", "TYPES"):
        p, t = _py_set(py, name), _ts_set(ts, name)
        drift = sorted((p - t) | (t - p))
        mark = "OK" if not drift else f"DRIFT {drift}"
        if drift:
            ok = False
        print(f"  {name}: jnl.py={len(p)} jfs.ts={len(t)}  {mark}")
    print("lockstep GREEN" if ok else "lockstep DRIFT — run validate.py")
    return 0 if ok else 1


def add(kind: str, token: str, dry: bool) -> int:
    pat, setname = GRAMMAR[kind]
    if not re.match(pat, token):
        print(f"'{token}' is not a valid {kind} token (must match {pat})")
        return 1
    py, ts = JNL_PY.read_text(), JFS_TS.read_text()
    if token in _py_set(py, setname) and token in _ts_set(ts, setname):
        print(f"'{token}' already present in both — nothing to do (idempotent).")
        return 0
    # jnl.py: insert right after the opening brace of the set literal.
    py2 = re.sub(rf"({setname} = \{{)", rf'\1"{token}", ', py, count=1)
    # jfs.ts: insert as the first member after the opening bracket.
    ts2 = re.sub(rf"(export const {setname} = new Set\(\[)", rf'\1\n  "{token}",', ts, count=1)
    if py2 == py or ts2 == ts:
        print(f"could not locate {setname} in one of the files — aborted, nothing written.")
        return 1
    print(f"+ {token} -> jnl.py {setname}\n+ {token} -> jfs.ts {setname}")
    if dry:
        print("dry-run — no files written.")
        return 0
    JNL_PY.write_text(py2)
    JFS_TS.write_text(ts2)
    print("written. NEXT: python core/JarvisMain/yggdrasil/tools/seed.py && "
          "python core/JarvisMain/yggdrasil/tools/validate.py")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Add a JNL grammar token in lockstep (jnl.py + jfs.ts).")
    ap.add_argument("--check", action="store_true", help="report lockstep status, write nothing")
    ap.add_argument("--add-domain", metavar="TOKEN", help="add a Domain token to both files")
    ap.add_argument("--add-type", metavar="TOKEN", help="add a Type token to both files")
    ap.add_argument("--dry-run", action="store_true", help="show the edits without writing")
    a = ap.parse_args()
    if a.check:
        return check()
    if a.add_domain:
        return add("domain", a.add_domain, a.dry_run)
    if a.add_type:
        return add("type", a.add_type, a.dry_run)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
