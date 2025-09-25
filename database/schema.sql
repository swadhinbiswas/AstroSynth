-- AstroSynth PostgreSQL schema v1.0.0
-- Mirrors backend/app/models + alembic 0001_initial
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) DEFAULT '',
  role VARCHAR(32) NOT NULL DEFAULT 'scientist' CHECK (role IN ('admin','scientist','viewer')),
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  mission VARCHAR(32) NOT NULL CHECK (mission IN ('kepler','k2','tess')),
  version VARCHAR(32) DEFAULT 'v1',
  rows_count INTEGER DEFAULT 0,
  storage_uri TEXT DEFAULT '',
  checksum VARCHAR(128) DEFAULT '',
  meta JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(128) NOT NULL,
  version VARCHAR(32) NOT NULL,
  algorithm VARCHAR(64) NOT NULL,
  metrics JSONB DEFAULT '{}',
  params JSONB DEFAULT '{}',
  artifact_uri TEXT DEFAULT '',
  is_active BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  model_id UUID REFERENCES models(id) ON DELETE SET NULL,
  input_features JSONB NOT NULL,
  predicted_class VARCHAR(32) NOT NULL,
  confidence DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  probabilities JSONB DEFAULT '{}',
  explanations JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  name VARCHAR(255) NOT NULL,
  config JSONB DEFAULT '{}',
  results JSONB DEFAULT '{}',
  status VARCHAR(32) DEFAULT 'completed',
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  title VARCHAR(255) NOT NULL,
  content_md TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prediction_id UUID REFERENCES predictions(id) ON DELETE SET NULL,
  user_label VARCHAR(32) NOT NULL,
  comment TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  actor VARCHAR(255) DEFAULT '',
  action VARCHAR(128) NOT NULL,
  resource VARCHAR(255) DEFAULT '',
  meta JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_datasets_mission ON datasets(mission);
CREATE INDEX ix_models_name ON models(name);
CREATE INDEX ix_predictions_class_created ON predictions(predicted_class, created_at);
CREATE INDEX ix_audit_action ON audit_logs(action);
CREATE INDEX ix_audit_created ON audit_logs(created_at);
CREATE INDEX ix_predictions_created ON predictions(created_at);
