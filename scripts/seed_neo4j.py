"""Seed Neo4j with JARVIS God System graph."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Load .env
for line in (BASE_DIR / ".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from neo4j import GraphDatabase

URI   = os.environ.get("NEO4J_URI",      "bolt://localhost:7687")
USER  = os.environ.get("NEO4J_USER",     "neo4j")
PASS  = os.environ.get("NEO4J_PASSWORD", "")

chaos       = json.loads((BASE_DIR / "chaos" / "chaos_seed.json").read_text())
god_systems = chaos.get("god_systems", {})
pipeline    = chaos.get("pipeline", {}).get("order", [])
parallel    = chaos.get("pipeline", {}).get("parallel", [])
forbidden   = chaos.get("interaction_graph", {}).get("forbidden_edges", [])
now         = lambda: datetime.now(timezone.utc).isoformat()

driver = GraphDatabase.driver(URI, auth=(USER, PASS))
driver.verify_connectivity()
print(f"Connected to {URI}")

nodes = edges = 0
with driver.session() as s:
    for name, data in god_systems.items():
        s.run(
            "MERGE (n:GodSystem {id: $id}) SET n += $props",
            id=name,
            props={
                "id":           name,
                "tier":         data.get("tier", ""),
                "function":     data.get("function", data.get("role", "")),
                "cannot":       json.dumps(data.get("cannot", [])),
                "always_active": data.get("always_active", False),
                "updated_at":   now(),
            }
        )
        nodes += 1

    for i in range(len(pipeline) - 1):
        a, b = pipeline[i], pipeline[i + 1]
        if a in god_systems and b in god_systems:
            s.run(
                "MATCH (a:GodSystem {id: $a}), (b:GodSystem {id: $b}) "
                "MERGE (a)-[:PIPELINE_NEXT {order: $o}]->(b)",
                a=a, b=b, o=i
            )
            edges += 1

    for sys_name in parallel:
        if sys_name in god_systems and "ODIN" in god_systems:
            s.run(
                "MATCH (a:GodSystem {id: $a}), (b:GodSystem {id: $b}) "
                "MERGE (a)-[:PARALLEL_WITH]->(b)",
                a="ODIN", b=sys_name
            )
            edges += 1

    for edge in forbidden:
        if len(edge) == 2 and edge[0] in god_systems and edge[1] in god_systems:
            s.run(
                "MATCH (a:GodSystem {id: $a}), (b:GodSystem {id: $b}) "
                "MERGE (a)-[:FORBIDDEN {reason: 'Gold Law constraint'}]->(b)",
                a=edge[0], b=edge[1]
            )
            edges += 1

driver.close()
print(f"Nodes upserted : {nodes}")
print(f"Edges upserted : {edges}")
print(f"Pipeline       : {' -> '.join(pipeline)}")
print(f"Parallel       : {', '.join(parallel)}")
print(f"Forbidden      : {len(forbidden)} edge(s)")
print("Graph seeded.")
