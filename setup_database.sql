-- Complete Trading Scanner Database Setup
-- Copy and paste this entire file into Supabase SQL Editor

-- Screened stocks (from Screener CSV)
create table screened_stocks (
  symbol text primary key,
  exchange text default 'NSE',
  added_at timestamptz default now(),
  meta jsonb
);

-- Daily candles (kept forever)
create table daily_candles (
  symbol text not null,
  ts date not null,
  open double precision,
  high double precision,
  low double precision,
  close double precision,
  volume double precision,
  primary key (symbol, ts)
);

create index idx_daily_candles_symbol_ts on daily_candles(symbol, ts desc);

-- Insight types (definition)
create table insight_types (
  id bigserial primary key,
  code text unique not null,
  name text not null,
  category text not null check (category in ('FORMULA','PATTERN','SENTIMENT')),
  description text,
  meta jsonb
);

-- Insights (outputs from logic modules)
create table insights (
  id bigserial primary key,
  symbol text not null references screened_stocks(symbol),
  insight_type_id bigint not null references insight_types(id),
  detected_on date not null,
  created_at timestamptz default now(),
  signal_type text check (signal_type in ('BUY','SELL','NEUTRAL')),
  price double precision,
  score double precision,
  attributes jsonb,
  unique(symbol, insight_type_id, detected_on)
);

create index idx_insights_symbol_date on insights(symbol, detected_on desc);

-- Insight images
create table insight_images (
  id bigserial primary key,
  insight_id bigint not null references insights(id) on delete cascade,
  storage_path text not null,
  img_url text not null,
  meta jsonb,
  created_at timestamptz default now()
);

-- Detected trade signals (main trade rows)
create table detected_signals (
  id bigserial primary key,
  symbol text not null references screened_stocks(symbol) on delete restrict,
  pattern text not null,
  signal_type text not null check (signal_type in ('BUY','SELL','NEUTRAL')),
  detected_on date not null,
  created_at timestamptz default now(),
  buy_price double precision,
  stop_loss double precision,
  target_price double precision,
  risk_reward double precision,
  support_levels double precision[],
  resistance_levels double precision[],
  extra jsonb
);

create index idx_detected_signals_symbol_detected_on on detected_signals(symbol, detected_on desc);

-- Images linked to detected_signals (chart images)
create table chart_images (
  id bigserial primary key,
  signal_id bigint not null references detected_signals(id) on delete cascade,
  symbol text not null,
  created_at timestamptz default now(),
  storage_path text not null,
  img_url text not null,
  meta jsonb
);

-- Combined daily score per stock
create table stock_daily_scores (
  id bigserial primary key,
  symbol text not null references screened_stocks(symbol),
  date date not null,
  combined_score double precision,
  details jsonb,
  created_at timestamptz default now(),
  unique(symbol, date)
);

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

-- Insert default insight types
insert into insight_types (code, name, category, description) values
('RSI_OVERSOLD', 'RSI Oversold', 'FORMULA', 'RSI below 30 indicating oversold condition'),
('RSI_OVERBOUGHT', 'RSI Overbought', 'FORMULA', 'RSI above 70 indicating overbought condition'),
('EMA_CROSS', 'EMA Crossover', 'FORMULA', 'Short EMA crossing above long EMA'),
('MACD_BULLISH', 'MACD Bullish', 'FORMULA', 'MACD line crossing above signal line'),
('BOLLINGER_SQUEEZE', 'Bollinger Squeeze', 'PATTERN', 'Low volatility squeeze pattern'),
('BREAKOUT', 'Breakout Pattern', 'PATTERN', 'Price breaking above resistance'),
('TWITTER_SENTIMENT', 'Twitter Sentiment', 'SENTIMENT', 'Aggregated Twitter sentiment analysis'),
('NEWS_SENTIMENT', 'News Sentiment', 'SENTIMENT', 'News sentiment analysis');
