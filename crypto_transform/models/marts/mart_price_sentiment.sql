-- mart_price_sentiment.sql
-- Final fact table for dashboards
-- Reads from gold_price_sentiment and selects the most useful columns
-- This is the table Power BI / Superset will query directly

SELECT
    ingestion_hour,
    last_updated,
    coin_id,
    symbol,
    name,
    current_price,
    market_cap,
    market_cap_rank,
    total_volume,
    high_24h,
    low_24h,
    price_change_24h,
    price_change_percentage_24h,
    circulating_supply,
    fear_greed_value,
    value_classification,
    volatility_category
FROM {{ source('gold', 'gold_price_sentiment') }}
WHERE coin_id IS NOT NULL
  AND current_price IS NOT NULL
