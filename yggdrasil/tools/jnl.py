"""JNL — Jarvis Navigation Language: grammar parser + validator.

Canonical address format (jfs/jnl-grammar.md):

    [Domain]-[System]-[Type]-[Log]-[Patch]-[Block]

Truth is the spec doc; this module is its executable mirror. Keep them in lockstep.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

# Canonical code tables (mirror of jfs/jnl-grammar.md).
DOMAINS = {"GS", "ARCH", "GOV", "IMPL", "PROJ", "GRID", "CONN", "AUD", "IDEA", "BRK", "LOG"}
TYPES = {"CORE", "SPEC", "PATCH", "RT", "IDX", "REG", "BIO", "LOG", "REVW"}

# Substrate + the 27 fixed God Systems. Do not add god systems (GL constraint).
# JFS family: kernel primitives (JNS/JNL/JSL/JMS) + status (JSS) + memory (JMMS/tiers)
# + dictionary (JD) + discovery (LAL) + language (JPL) + root (YGG).
SUBSTRATE = {
    "YGG", "JFS", "JNS", "JNL", "JSL", "JMS", "JD", "LAL", "JPL",
    "JSS",                              # status system
    "JMMS", "JSTM", "JLTM", "JATM",     # multimemory system + tiers
}

# JSS — Jarvis Status System. The governed lifecycle vocabulary for every object.
STATUSES = {"TASK", "EXPANSION", "ACTIVE", "INACTIVE", "ARCHIVED", "DEPRECATED"}

# Ontology classes (hygiene packet 1): what kind of object this is.
CLASSES = {"SYSTEM", "SPEC", "MODULE", "ENTITY", "EVENT", "REGISTRY"}

# MAIN = canonical core; SIDE = periphery (projects / ideas / breakthroughs / archived / deprecated).
TIERS = {"MAIN", "SIDE"}
GOD_SYSTEMS = {
    "AYR", "AEG", "ODN", "KRN", "SKD", "MNE", "HUG", "CHA",          # core 8
    "BFR", "HAL", "ATH", "NEM", "APO",                               # orchestration 5
    "LOK", "MER", "DAN", "ATL", "HER", "IRS", "PRO", "ARG", "JAN",   # governance 9
    "ERI", "ZEU", "POS", "HAD", "MIM",                               # cosmic 5
}
SYSTEMS = SUBSTRATE | GOD_SYSTEMS

JNL_RE = re.compile(r"^([A-Z]{2,4})-([A-Z0-9]{2,4})-([A-Z]{2,5})-(\d{4})(?:-P(\d{3})(?:-B(\d{3}))?)?$")


@dataclass(frozen=True)
class JNLAddress:
    domain: str
    system: str
    type: str
    log: str
    patch: str | None = None
    block: str | None = None

    def __str__(self) -> str:
        s = f"{self.domain}-{self.system}-{self.type}-{self.log}"
        if self.patch:
            s += f"-P{self.patch}"
            if self.block:
                s += f"-B{self.block}"
        return s


def parse(addr: str) -> JNLAddress:
    """Parse a JNL string into structured form. Raises ValueError with the reason."""
    m = JNL_RE.match(addr)
    if not m:
        raise ValueError(f"malformed JNL '{addr}': does not match grammar")
    domain, system, typ, log, patch, block = m.groups()
    if domain not in DOMAINS:
        raise ValueError(f"'{addr}': unknown Domain '{domain}' (allowed: {sorted(DOMAINS)})")
    if typ not in TYPES:
        raise ValueError(f"'{addr}': unknown Type '{typ}' (allowed: {sorted(TYPES)})")
    if domain == "GS" and system not in GOD_SYSTEMS:
        raise ValueError(f"'{addr}': '{system}' is not one of the 27 God Systems")
    # The kernel family (ARCH-<system>-CORE) is reserved for the 8 substrate primitives.
    # Other ARCH types (SPEC/RT/etc.) may name architecture docs freely.
    if domain == "ARCH" and typ == "CORE" and system not in SUBSTRATE:
        raise ValueError(f"'{addr}': '{system}' is not a substrate kernel primitive (ARCH-*-CORE is reserved)")
    return JNLAddress(domain, system, typ, log, patch, block)


def is_valid(addr: str) -> bool:
    try:
        parse(addr)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        try:
            print(f"OK   {a}  ->  {parse(a)!r}")
        except ValueError as e:
            print(f"FAIL {e}")
