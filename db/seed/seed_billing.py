import os
import random
import uuid
from datetime import datetime, timedelta, timezone

import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://atlas:atlas_dev@localhost:5432/atlas",
)


def seed_billing(count: int = 50) -> int:
    plans = ("free", "starter", "pro", "enterprise")
    error_codes = (None, None, "E-42", "E-17", "E-99")

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM billing_customers")
            for index in range(count):
                error_code = random.choice(error_codes)
                error_at = (
                    datetime.now(timezone.utc)
                    - timedelta(days=random.randint(1, 180))
                    if error_code
                    else None
                )
                cursor.execute(
                    """
                    INSERT INTO billing_customers
                        (id, name, plan, error_code, error_at, mrr_usd)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid.uuid4(),
                        f"Customer {index + 1}",
                        random.choice(plans),
                        error_code,
                        error_at,
                        round(random.uniform(25, 5000), 2),
                    ),
                )

    return count


if __name__ == "__main__":
    print(f"Seeded {seed_billing()} billing customers")
