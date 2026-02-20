-- OParl-Performance-Indexes
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(start_date DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_organization ON meetings(organization_id);
CREATE INDEX IF NOT EXISTS idx_papers_type ON papers(paper_type);
CREATE INDEX IF NOT EXISTS idx_papers_created ON papers(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_persons_organization ON persons(organization_id);

-- Volltext-Suche über alle OParl-Objekte
CREATE INDEX IF NOT EXISTS idx_papers_fts 
  ON papers USING gin(to_tsvector('german', coalesce(name,'') || ' ' || coalesce(description,'')));
  
CREATE INDEX IF NOT EXISTS idx_meetings_fts
  ON meetings USING gin(to_tsvector('german', coalesce(name,'') || ' ' || coalesce(description,'')));

-- Statistik-Views für Dashboard
CREATE OR REPLACE VIEW v_stats AS
SELECT
  (SELECT COUNT(*) FROM meetings WHERE start_date >= CURRENT_DATE - INTERVAL '30 days') AS meetings_last_30_days,
  (SELECT COUNT(*) FROM papers WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') AS papers_last_30_days,
  (SELECT COUNT(*) FROM persons WHERE active = true) AS active_persons;
