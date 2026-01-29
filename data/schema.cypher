// Supply Chain Graph Schema
// Run this against Neo4j after the DB is up (e.g. via browser at http://localhost:7474 or using the seed script).

// ----- Constraints (uniqueness; also create indexes) -----
CREATE CONSTRAINT company_id IF NOT EXISTS
FOR (n:Company) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT supplier_id IF NOT EXISTS
FOR (n:Supplier) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT factory_id IF NOT EXISTS
FOR (n:Factory) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT port_id IF NOT EXISTS
FOR (n:Port) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT country_id IF NOT EXISTS
FOR (n:Country) REQUIRE n.id IS UNIQUE;

// ----- Indexes for lookups and traversal -----
CREATE INDEX company_name IF NOT EXISTS
FOR (n:Company) ON (n.name);

CREATE INDEX supplier_tier IF NOT EXISTS
FOR (n:Supplier) ON (n.tier);

CREATE INDEX company_coords IF NOT EXISTS
FOR (n:Company) ON (n.lat, n.lon);

CREATE INDEX supplier_coords IF NOT EXISTS
FOR (n:Supplier) ON (n.lat, n.lon);

CREATE INDEX factory_coords IF NOT EXISTS
FOR (n:Factory) ON (n.lat, n.lon);

CREATE INDEX port_coords IF NOT EXISTS
FOR (n:Port) ON (n.lat, n.lon);

CREATE INDEX country_code IF NOT EXISTS
FOR (n:Country) ON (n.code);
