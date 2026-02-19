-- aitema|RIS - Initial Database Setup
-- This script runs when the PostgreSQL container starts for the first time.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create keycloak schema (used by Keycloak service)
CREATE SCHEMA IF NOT EXISTS keycloak;

-- Grant permissions
GRANT ALL ON SCHEMA public TO ris;
GRANT ALL ON SCHEMA keycloak TO ris;
