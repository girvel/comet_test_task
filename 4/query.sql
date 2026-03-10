SELECT phrase, groupArray(tuple(hour, views_in_hour)) AS views_by_hour
FROM (
    SELECT 
        phrase, 
        toHour(dt) AS hour,
        max(views) AS max_views,
        -- Subtract the previous hour's max cumulative views to get the delta for this hour
        max_views - lagInFrame(max_views, 1, min(views)) OVER (PARTITION BY phrase ORDER BY hour) AS views_in_hour
    FROM phrases_views
    WHERE campaign_id = 1111111 AND toDate(dt) = '2025-01-01'
    GROUP BY phrase, toHour(dt) AS hour
    ORDER BY hour DESCENDING
)
WHERE views_in_hour > 0  -- Filter out 0-view hours to match the exact output requested
GROUP BY phrase;
