DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
  id bigint PRIMARY KEY,
  last_modified bigint NOT NULL DEFAULT 0,
  data jsonb NOT NULL DEFAULT '{}'
);
CREATE TABLE leads (
  id bigint PRIMARY KEY,
  last_modified bigint NOT NULL DEFAULT 0,
  data jsonb NOT NULL DEFAULT '{}'
);

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all" ON clients FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "allow_all" ON leads FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER PUBLICATION supabase_realtime ADD TABLE clients, leads;