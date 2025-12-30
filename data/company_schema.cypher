// Company Knowledge Base Schema
// Entities: Employee, Department, Project, Skill, Document

// ============================================================
// CONSTRAINTS (Enforce uniqueness)
// ============================================================

// Employee constraints
CREATE CONSTRAINT employee_email IF NOT EXISTS 
  FOR (e:Employee) REQUIRE e.email IS UNIQUE;

// Department constraints
CREATE CONSTRAINT department_name IF NOT EXISTS 
  FOR (d:Department) REQUIRE d.name IS UNIQUE;

// Project constraints
CREATE CONSTRAINT project_id IF NOT EXISTS 
  FOR (p:Project) REQUIRE p.project_id IS UNIQUE;

// Skill constraints
CREATE CONSTRAINT skill_name IF NOT EXISTS 
  FOR (s:Skill) REQUIRE s.name IS UNIQUE;

// Document constraints
CREATE CONSTRAINT document_id IF NOT EXISTS 
  FOR (doc:Document) REQUIRE doc.doc_id IS UNIQUE;

// ============================================================
// INDEXES (Optimize queries)
// ============================================================

// Employee indexes
CREATE INDEX employee_name IF NOT EXISTS 
  FOR (e:Employee) ON (e.name);

CREATE INDEX employee_title IF NOT EXISTS 
  FOR (e:Employee) ON (e.title);

// Project indexes
CREATE INDEX project_name IF NOT EXISTS 
  FOR (p:Project) ON (p.name);

CREATE INDEX project_status IF NOT EXISTS 
  FOR (p:Project) ON (p.status);

// Document indexes
CREATE INDEX document_title IF NOT EXISTS 
  FOR (doc:Document) ON (doc.title);

CREATE INDEX document_type IF NOT EXISTS 
  FOR (doc:Document) ON (doc.type);

// ============================================================
// FULL-TEXT SEARCH INDEXES
// ============================================================

// Search employees by name, bio, title
CREATE FULLTEXT INDEX employee_search IF NOT EXISTS
  FOR (e:Employee) ON EACH [e.name, e.bio, e.title];

// Search documents by title and content
CREATE FULLTEXT INDEX document_search IF NOT EXISTS
  FOR (doc:Document) ON EACH [doc.title, doc.content, doc.summary];

// Search projects by name and description
CREATE FULLTEXT INDEX project_search IF NOT EXISTS
  FOR (p:Project) ON EACH [p.name, p.description];
