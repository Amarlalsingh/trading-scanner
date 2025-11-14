-- Add test stocks to see the app working
INSERT INTO screened_stocks (symbol, exchange) VALUES 
('RELIANCE', 'NSE'),
('TCS', 'NSE'),
('INFY', 'NSE'),
('HDFCBANK', 'NSE'),
('ICICIBANK', 'NSE');

-- Add some test fundamental data
INSERT INTO fundamentals (symbol, company_name, market_cap, pe_ratio, sector) VALUES 
('RELIANCE', 'Reliance Industries Limited', 1500000000000, 25.5, 'Energy'),
('TCS', 'Tata Consultancy Services', 1200000000000, 28.2, 'Information Technology'),
('INFY', 'Infosys Limited', 800000000000, 24.8, 'Information Technology'),
('HDFCBANK', 'HDFC Bank Limited', 900000000000, 18.5, 'Financial Services'),
('ICICIBANK', 'ICICI Bank Limited', 700000000000, 16.2, 'Financial Services');
