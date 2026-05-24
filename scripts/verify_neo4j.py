import os
from pathlib import Path

for line in (Path(__file__).parent.parent / ".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from neo4j import GraphDatabase
d = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.environ["NEO4J_PASSWORD"]))
with d.session() as s:
    rows = s.run(
        "MATCH (n:GodSystem)-[r]->(m:GodSystem) "
        "RETURN n.id AS a, type(r) AS rel, m.id AS b ORDER BY rel, a"
    ).data()
    for r in rows:
        print(f"  {r['a']:12} -[{r['rel']:14}]-> {r['b']}")
    count = s.run("MATCH (n:GodSystem) RETURN count(n) AS c").single()["c"]
    print(f"\nTotal GodSystem nodes: {count}")
d.close()
