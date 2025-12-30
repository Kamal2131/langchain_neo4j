// Neo4j Schema Definition
// Project-Technology-Person Knowledge Graph

// Create constraints for unique identifiers
CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT project_name IF NOT EXISTS FOR (pr:Project) REQUIRE pr.name IS UNIQUE;
CREATE CONSTRAINT tech_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE;

// Create indexes for better query performance
CREATE INDEX person_email IF NOT EXISTS FOR (p:Person) ON (p.email);
CREATE INDEX project_status IF NOT EXISTS FOR (pr:Project) ON (pr.status);
CREATE INDEX tech_category IF NOT EXISTS FOR (t:Technology) ON (t.category);
