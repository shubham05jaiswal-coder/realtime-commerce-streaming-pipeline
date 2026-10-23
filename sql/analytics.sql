-- Purchase revenue and count by hour
SELECT date_trunc('hour', event_time) AS event_hour,
       COUNT(*) AS purchase_events, SUM(revenue) AS gross_revenue
FROM commerce_events
WHERE event_type = 'purchase'
GROUP BY 1 ORDER BY 1 DESC;

-- Unique sessions by event type (simple funnel view)
SELECT event_type, COUNT(DISTINCT session_id) AS sessions
FROM commerce_events
GROUP BY event_type
ORDER BY CASE event_type WHEN 'view' THEN 1 WHEN 'add_to_cart' THEN 2
         WHEN 'checkout' THEN 3 WHEN 'purchase' THEN 4 ELSE 5 END;

-- Revenue by product category
SELECT category, COUNT(*) AS purchases, SUM(revenue) AS gross_revenue
FROM commerce_events WHERE event_type = 'purchase'
GROUP BY category ORDER BY gross_revenue DESC;

-- Daily active users
SELECT date_trunc('day', event_time)::date AS event_date,
       COUNT(DISTINCT user_id) AS daily_active_users
FROM commerce_events GROUP BY 1 ORDER BY 1 DESC;
