-- mart_volatility_summary.sql
-- Aggregated summary table: one row per sentiment classification
-- Answers the core question: does fear/greed correlate with price volatility?
-- This powers the Hype-to-Volume Matrix and Sentiment Heatmap dashboards

SELECT
    value_classification,
    fear_greed_value,
    volatility_category,
    COUNT(*)                                        AS total_readings,
    ROUND(AVG(price_change_percentage_24h), 4)      AS avg_price_change_pct,
    ROUND(MAX(price_change_percentage_24h), 4)      AS max_price_change_pct,
    ROUND(MIN(price_change_percentage_24h), 4)      AS min_price_change_pct,
    ROUND(AVG(current_price), 2)                    AS avg_price,
    ROUND(AVG(total_volume), 0)                     AS avg_volume,
    ROUND(AVG(market_cap), 0)                       AS avg_market_cap
FROM {{ source('gold', 'gold_price_sentiment') }}
WHERE fear_greed_value IS NOT NULL
GROUP BY value_classification, fear_greed_value, volatility_category
ORDER BY fear_greed_value ASC
