CREATE TABLE IF NOT EXISTS tickers (
  id SERIAL PRIMARY KEY,
  ticker VARCHAR(20) NOT NULL UNIQUE,
  date DATE NOT NULL,
  pct_change_current_quarter NUMERIC NOT NULL,
  pct_change_next_quarter NUMERIC NOT NULL,
  pct_change_current_fiscal_year NUMERIC NOT NULL,
  num_current_fiscal_year_estimates NUMERIC NOT NULL,
  count INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS uploads (
  id SERIAL PRIMARY KEY,
  upload_date DATE NOT NULL UNIQUE,
  status VARCHAR(20) NOT NULL DEFAULT 'success'
);
