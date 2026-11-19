TABLE_DDL = """
CREATE TABLE billing_customers (
  id UUID,
  name TEXT,
  plan TEXT,
  error_code TEXT,
  error_at TIMESTAMPTZ,
  mrr_usd NUMERIC
);
"""

FEW_SHOT_EXAMPLES = [
    (
        "How many enterprise customers are there?",
        "SELECT COUNT(*) AS customer_count FROM billing_customers "
        "WHERE plan = 'enterprise';",
    ),
    (
        "List pro customers who hit E-42.",
        "SELECT name, mrr_usd FROM billing_customers "
        "WHERE plan = 'pro' AND error_code = 'E-42';",
    ),
    (
        "What is total MRR for enterprise customers?",
        "SELECT SUM(mrr_usd) AS total_mrr FROM billing_customers "
        "WHERE plan = 'enterprise';",
    ),
    (
        "Show customers with errors this month.",
        "SELECT name, plan, error_code FROM billing_customers "
        "WHERE error_at >= date_trunc('month', CURRENT_TIMESTAMP);",
    ),
    (
        "List the five highest MRR customers.",
        "SELECT name, plan, mrr_usd FROM billing_customers "
        "ORDER BY mrr_usd DESC LIMIT 5;",
    ),
]
