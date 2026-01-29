# Supply Chain Graph Schema

Nodes and relationships used for Tier-1 to Tier-4 supply chain and risk analysis.

---

## Node types

| Label    | Description        | Key properties                                      |
|----------|--------------------|-----------------------------------------------------|
| `Company`  | Focal or customer company | `id`, `name`, `lat`, `lon` (HQ or primary location) |
| `Supplier` | Tier-1 to Tier-4 supplier | `id`, `name`, `tier` (1–4), `lat`, `lon`           |
| `Factory`  | Production site    | `id`, `name`, `lat`, `lon`                          |
| `Port`     | Logistics node     | `id`, `name`, `lat`, `lon`, `code`                  |
| `Country`  | Geography          | `id`, `name`, `code` (e.g. US, CN), optional `lat`, `lon` |

All location-bearing nodes use `lat` and `lon` (WGS84) for map visualization.

---

## Relationship types

| Type          | From → To       | Meaning                          | Typical properties   |
|---------------|-----------------|----------------------------------|----------------------|
| `SUPPLIES_TO` | Supplier → Company, or Supplier → Supplier | Direct supply relationship | `product`, `volume` (optional) |
| `DEPENDS_ON`  | Company → Supplier, or Supplier → Supplier | Dependency (who depends on whom) | `product` (optional) |
| `SHIPS_VIA`   | Supplier/Factory → Port, or Port → Port     | Logistics route                 | —                    |
| `LOCATED_IN`  | Company, Supplier, Factory, Port → Country | Geographic containment          | —                    |

Traversals use these to compute upstream (who supplies) and downstream (who is impacted).

---

## Example Cypher queries

### Upstream from a company (variable depth)

All suppliers and related nodes that feed into a given company, up to `depth` hops:

```cypher
MATCH path = (c:Company { id: $company_id })<-[:SUPPLIES_TO|DEPENDS_ON*1..4]-(upstream)
WHERE upstream:Supplier OR upstream:Factory
RETURN path;
```

Or returning nodes and relationships for the map (nodes with coords, edges for drawing):

```cypher
MATCH path = (c:Company { id: $company_id })<-[:SUPPLIES_TO|DEPENDS_ON*1..4]-(upstream)
UNWIND nodes(path) AS n
UNWIND relationships(path) AS r
RETURN DISTINCT n, r;
```

### Downstream impact from a port closure

Nodes and paths that depend on a given port (shipments through it):

```cypher
MATCH path = (p:Port { id: $port_id })<-[:SHIPS_VIA*1..5]-(origin)-[:SUPPLIES_TO|DEPENDS_ON*0..4]->(downstream)
WHERE downstream:Company OR downstream:Supplier
RETURN path;
```

---

## Constraints and indexes

Defined in `data/schema.cypher`:

- **Uniqueness:** `id` on `Company`, `Supplier`, `Factory`, `Port`, `Country`.
- **Lookups:** `Company.name`, `Supplier.tier`, `Country.code`, and coordinate indexes where needed for geospatial results.

Run `schema.cypher` once after Neo4j is up, before loading mock data.
