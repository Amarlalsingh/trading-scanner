-- Add fundamentals table to existing schema
-- Run this after the main supabase_init.sql

-- Fundamental data table
create table fundamentals (
  symbol text primary key references screened_stocks(symbol),
  company_name text,
  market_cap bigint,
  roe double precision,
  pe_ratio double precision,
  pb_ratio double precision,
  eps double precision,
  industry text,
  sector text,
  updated_at timestamptz default now(),
  meta jsonb
);

create index idx_fundamentals_sector on fundamentals(sector);
create index idx_fundamentals_industry on fundamentals(industry);
create index idx_fundamentals_market_cap on fundamentals(market_cap desc);
