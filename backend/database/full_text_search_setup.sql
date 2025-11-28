-- Full-Text Search Setup for AISET
-- DO-178C Traceability: REQ-DB-054
--
-- This script sets up PostgreSQL full-text search capabilities for AISET.
-- Provides fast, ranked search across requirements, design components, test cases,
-- and other textual content.
--
-- Features:
-- - Full-text search indexes using tsvector
-- - Custom search configurations
-- - Weighted ranking (title > description > content)
-- - Search triggers for automatic index updates

-- Create full-text search configuration (English language)
CREATE TEXT SEARCH CONFIGURATION aiset_search (COPY = pg_catalog.english);

-- Add full-text search columns to requirements table
ALTER TABLE requirements
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Create index for requirements search
CREATE INDEX IF NOT EXISTS requirements_search_idx
ON requirements USING GIN (search_vector);

-- Trigger function to update search vector
CREATE OR REPLACE FUNCTION requirements_search_trigger() RETURNS trigger AS $$
begin
  new.search_vector :=
    setweight(to_tsvector('aiset_search', coalesce(new.requirement_id,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.title,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.description,'')), 'B') ||
    setweight(to_tsvector('aiset_search', coalesce(new.acceptance_criteria,'')), 'C') ||
    setweight(to_tsvector('aiset_search', coalesce(new.rationale,'')), 'D');
  return new;
end
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS requirements_search_update ON requirements;
CREATE TRIGGER requirements_search_update
BEFORE INSERT OR UPDATE ON requirements
FOR EACH ROW EXECUTE FUNCTION requirements_search_trigger();

-- Update existing requirements
UPDATE requirements SET search_vector =
  setweight(to_tsvector('aiset_search', coalesce(requirement_id,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(title,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(description,'')), 'B') ||
  setweight(to_tsvector('aiset_search', coalesce(acceptance_criteria,'')), 'C') ||
  setweight(to_tsvector('aiset_search', coalesce(rationale,'')), 'D');

-- Add full-text search to design_components
ALTER TABLE design_components
ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE INDEX IF NOT EXISTS design_components_search_idx
ON design_components USING GIN (search_vector);

CREATE OR REPLACE FUNCTION design_components_search_trigger() RETURNS trigger AS $$
begin
  new.search_vector :=
    setweight(to_tsvector('aiset_search', coalesce(new.component_id,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.name,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.description,'')), 'B') ||
    setweight(to_tsvector('aiset_search', coalesce(new.design_rationale,'')), 'C');
  return new;
end
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS design_components_search_update ON design_components;
CREATE TRIGGER design_components_search_update
BEFORE INSERT OR UPDATE ON design_components
FOR EACH ROW EXECUTE FUNCTION design_components_search_trigger();

UPDATE design_components SET search_vector =
  setweight(to_tsvector('aiset_search', coalesce(component_id,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(name,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(description,'')), 'B') ||
  setweight(to_tsvector('aiset_search', coalesce(design_rationale,'')), 'C');

-- Add full-text search to test_cases
ALTER TABLE test_cases
ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE INDEX IF NOT EXISTS test_cases_search_idx
ON test_cases USING GIN (search_vector);

CREATE OR REPLACE FUNCTION test_cases_search_trigger() RETURNS trigger AS $$
begin
  new.search_vector :=
    setweight(to_tsvector('aiset_search', coalesce(new.test_id,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.title,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.description,'')), 'B') ||
    setweight(to_tsvector('aiset_search', coalesce(new.test_procedure,'')), 'C') ||
    setweight(to_tsvector('aiset_search', coalesce(new.expected_result,'')), 'C');
  return new;
end
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS test_cases_search_update ON test_cases;
CREATE TRIGGER test_cases_search_update
BEFORE INSERT OR UPDATE ON test_cases
FOR EACH ROW EXECUTE FUNCTION test_cases_search_trigger();

UPDATE test_cases SET search_vector =
  setweight(to_tsvector('aiset_search', coalesce(test_id,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(title,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(description,'')), 'B') ||
  setweight(to_tsvector('aiset_search', coalesce(test_procedure,'')), 'C') ||
  setweight(to_tsvector('aiset_search', coalesce(expected_result,'')), 'C');

-- Add full-text search to configuration_items
ALTER TABLE configuration_items
ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE INDEX IF NOT EXISTS configuration_items_search_idx
ON configuration_items USING GIN (search_vector);

CREATE OR REPLACE FUNCTION configuration_items_search_trigger() RETURNS trigger AS $$
begin
  new.search_vector :=
    setweight(to_tsvector('aiset_search', coalesce(new.item_id,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.name,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.description,'')), 'B') ||
    setweight(to_tsvector('aiset_search', coalesce(new.part_number,'')), 'B') ||
    setweight(to_tsvector('aiset_search', coalesce(new.supplier,'')), 'C');
  return new;
end
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS configuration_items_search_update ON configuration_items;
CREATE TRIGGER configuration_items_search_update
BEFORE INSERT OR UPDATE ON configuration_items
FOR EACH ROW EXECUTE FUNCTION configuration_items_search_trigger();

UPDATE configuration_items SET search_vector =
  setweight(to_tsvector('aiset_search', coalesce(item_id,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(name,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(description,'')), 'B') ||
  setweight(to_tsvector('aiset_search', coalesce(part_number,'')), 'B') ||
  setweight(to_tsvector('aiset_search', coalesce(supplier,'')), 'C');

-- Add full-text search to projects
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE INDEX IF NOT EXISTS projects_search_idx
ON projects USING GIN (search_vector);

CREATE OR REPLACE FUNCTION projects_search_trigger() RETURNS trigger AS $$
begin
  new.search_vector :=
    setweight(to_tsvector('aiset_search', coalesce(new.project_code,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.name,'')), 'A') ||
    setweight(to_tsvector('aiset_search', coalesce(new.description,'')), 'B');
  return new;
end
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS projects_search_update ON projects;
CREATE TRIGGER projects_search_update
BEFORE INSERT OR UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION projects_search_trigger();

UPDATE projects SET search_vector =
  setweight(to_tsvector('aiset_search', coalesce(project_code,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(name,'')), 'A') ||
  setweight(to_tsvector('aiset_search', coalesce(description,'')), 'B');

-- Create unified search view for cross-entity search
CREATE OR REPLACE VIEW unified_search_view AS
SELECT
    'requirement' as entity_type,
    id,
    requirement_id as entity_id,
    title,
    description,
    project_id,
    search_vector
FROM requirements
UNION ALL
SELECT
    'design_component' as entity_type,
    id,
    component_id as entity_id,
    name as title,
    description,
    project_id,
    search_vector
FROM design_components
UNION ALL
SELECT
    'test_case' as entity_type,
    id,
    test_id as entity_id,
    title,
    description,
    project_id,
    search_vector
FROM test_cases
UNION ALL
SELECT
    'configuration_item' as entity_type,
    id,
    item_id as entity_id,
    name as title,
    description,
    project_id,
    search_vector
FROM configuration_items
UNION ALL
SELECT
    'project' as entity_type,
    id,
    project_code as entity_id,
    name as title,
    description,
    id as project_id,
    search_vector
FROM projects;

-- Search function with ranking
CREATE OR REPLACE FUNCTION search_aiset(
    search_query text,
    entity_types text[] DEFAULT ARRAY['requirement', 'design_component', 'test_case', 'configuration_item', 'project'],
    project_filter integer DEFAULT NULL,
    result_limit integer DEFAULT 50
)
RETURNS TABLE (
    entity_type text,
    id integer,
    entity_id text,
    title text,
    description text,
    project_id integer,
    rank real
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.entity_type,
        v.id,
        v.entity_id,
        v.title,
        v.description,
        v.project_id,
        ts_rank(v.search_vector, to_tsquery('aiset_search', search_query)) as rank
    FROM unified_search_view v
    WHERE v.search_vector @@ to_tsquery('aiset_search', search_query)
        AND v.entity_type = ANY(entity_types)
        AND (project_filter IS NULL OR v.project_id = project_filter)
    ORDER BY rank DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- SELECT * FROM search_aiset('safety & critical');
-- SELECT * FROM search_aiset('software', ARRAY['requirement'], 1);
