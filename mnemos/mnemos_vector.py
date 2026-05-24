"""
MNEMOS Vector Layer v1.0
Semantic memory for JARVIS using nomic-embed-text via Ollama.

Turns every session, PROMETHEUS entry, and God System definition
into a vector. Retrieval becomes semantic rather than chronological.
ERIS weights results by alignment — low entropy sessions ranked higher.

No numpy required. Pure Python cosine similarity.
Ollama must be running with nomic-embed-text pulled.

Usage:
    from mnemos_vector import MNEMOSVector
    mnemos = MNEMOSVector()
    mnemos.store("session_001", "session", "Built JARVIS MCP server", entropy=0.129)
    results = mnemos.search("what did we build for the MCP layer")
"""

import json
import math
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL      = "nomic-embed-text"
DB_PATH          = Path(__file__).parent.parent / "chaos" / "mnemos_vectors.db"


# ─────────────────────────────────────────────────────────────────────────────
# VECTOR MATH — pure Python, no numpy
# ─────────────────────────────────────────────────────────────────────────────

def dot(a: list, b: list) -> float:
    return sum(x * y for x, y in zip(a, b))

def magnitude(v: list) -> float:
    return math.sqrt(sum(x * x for x in v))

def cosine_similarity(a: list, b: list) -> float:
    mag_a = magnitude(a)
    mag_b = magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot(a, b) / (mag_a * mag_b)

def eris_weight(similarity: float, entropy: float) -> float:
    """
    ERIS priority weighting.
    Low entropy sessions are more aligned with mission.
    They rank higher in retrieval even at slightly lower similarity.
    weight = similarity * (1 - entropy * 0.3)
    """
    return similarity * (1.0 - entropy * 0.3)


# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDING — calls Ollama nomic-embed-text
# ─────────────────────────────────────────────────────────────────────────────

def embed(text: str) -> list:
    """
    Embed text using nomic-embed-text via Ollama.
    Returns a list of floats (768-dimensional vector).
    Raises ConnectionError if Ollama is not running.
    """
    payload = json.dumps({
        "model": EMBED_MODEL,
        "prompt": text
    }).encode()

    req = urllib.request.Request(
        OLLAMA_EMBED_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data["embedding"]
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Ollama not reachable at {OLLAMA_EMBED_URL}. "
            f"Make sure Ollama is running. Error: {e}"
        )
    except KeyError:
        raise ValueError("Ollama returned unexpected response — no 'embedding' field")


# ─────────────────────────────────────────────────────────────────────────────
# MNEMOS VECTOR STORE
# ─────────────────────────────────────────────────────────────────────────────

class MNEMOSVector:
    """
    Semantic memory layer for JARVIS.

    Stores entries as vectors. Retrieval uses cosine similarity
    weighted by ERIS entropy score — aligned sessions rank higher.

    Source types:
        session     — sealed session narratives
        prometheus  — rationale ledger entries
        god_system  — God System definitions from CHAOS
        checkpoint  — mid-session snapshots
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vector_store (
                    id          TEXT PRIMARY KEY,
                    source_id   TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    text        TEXT NOT NULL,
                    vector_json TEXT NOT NULL,
                    entropy     REAL DEFAULT 0.0,
                    platform    TEXT DEFAULT '',
                    timestamp   TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_type
                ON vector_store(source_type)
            """)
            conn.commit()

    def store(
        self,
        source_id:   str,
        source_type: str,
        text:        str,
        entropy:     float = 0.0,
        platform:    str   = ""
    ) -> dict:
        """
        Embed text and store in vector DB.
        Returns the stored entry metadata.
        """
        vector = embed(text)
        entry_id = f"{source_type}:{source_id}"
        ts = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO vector_store
                (id, source_id, source_type, text, vector_json, entropy, platform, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                source_id,
                source_type,
                text,
                json.dumps(vector),
                entropy,
                platform,
                ts
            ))
            conn.commit()

        return {
            "id":          entry_id,
            "source_type": source_type,
            "text":        text[:80] + "..." if len(text) > 80 else text,
            "entropy":     entropy,
            "timestamp":   ts,
            "vector_dims": len(vector)
        }

    def search(
        self,
        query:       str,
        limit:       int   = 5,
        source_type: str   = None,
        eris_weight_on: bool = True
    ) -> list:
        """
        Semantic search over stored memories.
        Returns entries ranked by cosine similarity,
        weighted by ERIS entropy score if eris_weight_on=True.
        """
        query_vector = embed(query)

        with sqlite3.connect(self.db_path) as conn:
            if source_type:
                rows = conn.execute("""
                    SELECT id, source_id, source_type, text, vector_json, entropy, platform, timestamp
                    FROM vector_store WHERE source_type = ?
                """, (source_type,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT id, source_id, source_type, text, vector_json, entropy, platform, timestamp
                    FROM vector_store
                """).fetchall()

        if not rows:
            return []

        scored = []
        for row in rows:
            id_, source_id, stype, text, vec_json, entropy, platform, ts = row
            stored_vector = json.loads(vec_json)
            sim = cosine_similarity(query_vector, stored_vector)
            score = eris_weight(sim, entropy) if eris_weight_on else sim
            scored.append({
                "id":          id_,
                "source_id":   source_id,
                "source_type": stype,
                "text":        text,
                "similarity":  round(sim, 4),
                "eris_score":  round(score, 4),
                "entropy":     entropy,
                "platform":    platform,
                "timestamp":   ts
            })

        scored.sort(key=lambda x: x["eris_score"], reverse=True)
        return scored[:limit]

    def store_god_systems(self, chaos_seed: dict) -> int:
        """
        Embed all God System definitions from CHAOS seed.
        Called once at server startup to make system knowledge searchable.
        Returns count of systems stored.
        """
        systems = chaos_seed.get("god_systems", {})
        count   = 0
        for name, data in systems.items():
            text = f"{name}: {data.get('function', data.get('role', ''))} [{data.get('tier', '')}]"
            try:
                self.store(
                    source_id=name,
                    source_type="god_system",
                    text=text,
                    entropy=0.0
                )
                count += 1
            except Exception:
                pass
        return count

    def store_session(self, session_entry: dict) -> dict:
        """
        Embed and store a sealed session entry.
        Called automatically by jarvis_end.
        """
        text = f"{session_entry.get('narrative', '')} platform={session_entry.get('platform', '')}"
        return self.store(
            source_id=session_entry.get("session_id", "unknown"),
            source_type="session",
            text=text,
            entropy=session_entry.get("entropy", 0.0),
            platform=session_entry.get("platform", "")
        )

    def store_prometheus(self, prometheus_entry: dict) -> dict:
        """
        Embed and store a PROMETHEUS rationale entry.
        Called automatically by jarvis_log.
        """
        text = f"{prometheus_entry.get('decision', '')} — {prometheus_entry.get('rationale', '')}"
        return self.store(
            source_id=prometheus_entry.get("id", "unknown"),
            source_type="prometheus",
            text=text,
            entropy=0.0,
            platform=""
        )

    def count(self, source_type: str = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            if source_type:
                return conn.execute(
                    "SELECT COUNT(*) FROM vector_store WHERE source_type = ?",
                    (source_type,)
                ).fetchone()[0]
            return conn.execute("SELECT COUNT(*) FROM vector_store").fetchone()[0]

    def stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT source_type, COUNT(*) as n
                FROM vector_store GROUP BY source_type
            """).fetchall()
        return {r[0]: r[1] for r in rows}


# ─────────────────────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("MNEMOS Vector Layer v1.0")
    print("Testing connection to Ollama nomic-embed-text...")

    try:
        v = embed("JARVIS mission: build useful AI workflows with explicit human authority")
        print(f"✓ Embedding working — {len(v)} dimensions")
    except ConnectionError as e:
        print(f"✗ {e}")
        exit(1)

    mnemos = MNEMOSVector()
    print(f"✓ Vector DB initialized at {mnemos.db_path}")

    # Store test entries
    mnemos.store("test_001", "session", "Built JARVIS MCP server, 27 systems loaded", entropy=0.129, platform="claude")
    mnemos.store("test_002", "session", "Pachinko Bounce GDD v0.4 complete, RGB ball system", entropy=0.100, platform="claude")
    mnemos.store("test_003", "prometheus", "AEGIS runs before ODIN — constraints first routing second", entropy=0.0)
    mnemos.store("test_004", "session", "OpenCode connected to Ollama local Qwen 7B", entropy=0.129, platform="claude")

    print(f"✓ Stored 4 test entries")
    print(f"  Total vectors: {mnemos.count()}")

    # Search test
    print()
    print("Search: 'what did we build for the MCP server'")
    results = mnemos.search("what did we build for the MCP server", limit=3)
    for r in results:
        print(f"  [{r['eris_score']:.3f}] {r['text'][:60]}")

    print()
    print("Search: 'game development Pachinko'")
    results = mnemos.search("game development Pachinko", limit=3)
    for r in results:
        print(f"  [{r['eris_score']:.3f}] {r['text'][:60]}")

    print()
    print(f"Stats: {mnemos.stats()}")
    print("✓ MNEMOS Vector Layer operational")
