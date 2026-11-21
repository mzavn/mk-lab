CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('owner', 'manager', 'accountant', 'member')),
  password_hash TEXT NOT NULL,
  totp_secret TEXT,
  locked INTEGER NOT NULL DEFAULT 0,
  failed_logins INTEGER NOT NULL DEFAULT 0,
  blocked_until INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  expires_at INTEGER NOT NULL
);

CREATE TABLE projects (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  name TEXT NOT NULL,
  budget INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived'))
);

CREATE TABLE periods (
  company_id INTEGER NOT NULL REFERENCES companies(id),
  period TEXT NOT NULL,
  closed INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (company_id, period)
);

CREATE TABLE invoices (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  project_id INTEGER NOT NULL REFERENCES projects(id),
  customer_name TEXT NOT NULL,
  amount INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft', 'issued', 'paid', 'void')),
  period TEXT NOT NULL,
  issued_at INTEGER
);

CREATE TABLE invoice_lines (
  id INTEGER PRIMARY KEY,
  invoice_id INTEGER NOT NULL REFERENCES invoices(id),
  description TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price INTEGER NOT NULL
);

CREATE TABLE payments (
  id INTEGER PRIMARY KEY,
  event_id TEXT UNIQUE,
  invoice_id INTEGER NOT NULL REFERENCES invoices(id),
  amount INTEGER NOT NULL,
  at INTEGER NOT NULL
);

CREATE TABLE refunds (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  invoice_id INTEGER NOT NULL REFERENCES invoices(id),
  amount INTEGER NOT NULL,
  created_by INTEGER NOT NULL REFERENCES users(id),
  at INTEGER NOT NULL
);

CREATE TABLE share_links (
  key_hash TEXT PRIMARY KEY,
  invoice_id INTEGER NOT NULL REFERENCES invoices(id),
  expires_at INTEGER NOT NULL
);

CREATE TABLE confirmations (
  code_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  action TEXT NOT NULL,
  subject TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  used INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  action TEXT NOT NULL,
  data TEXT NOT NULL,
  at INTEGER NOT NULL
);
