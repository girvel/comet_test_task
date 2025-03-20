SELECT phrase, groupArray(t) views_by_hour FROM (
    SELECT phrase, tuple(hour, sum(views)) AS t
    FROM phrases_views
    WHERE campaign_id = 1111111
    AND toDate(dt) = toDate('2025-01-01') /* let's pretend today is 2025-01-01 */
    GROUP BY toHour(dt) AS hour, phrase
    ORDER BY hour DESCENDING
)
GROUP BY phrase;
