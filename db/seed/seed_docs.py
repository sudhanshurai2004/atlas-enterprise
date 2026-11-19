import os

import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://atlas:atlas_dev@localhost:5432/atlas",
)


def seed() -> int:
    inserted_chunks = 0

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            for document_number in range(1, 21):
                source_type = "ticket" if document_number % 2 == 0 else "wiki"

                title = f"Runbook {document_number}: Database Operations"
                gcs_uri = f"local://data/runbook_{document_number:02d}.txt"

                cursor.execute(
                    """
                    INSERT INTO documents (source_type, gcs_uri, title, metadata)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (gcs_uri) DO UPDATE
                    SET title = EXCLUDED.title,
                        metadata = EXCLUDED.metadata
                    RETURNING id
                    """,
                    (source_type, gcs_uri, title, '{"seed": true}'),
                )
                document_id = cursor.fetchone()[0]

                for chunk_index in range(5):
                    content = (
                        f"Runbook {document_number} section {chunk_index + 1}: "
                        "Database credentials must be rotated, audit logs reviewed, "
                        "and failover procedures tested. Incident E-42 requires "
                        "customer notification and a rollback if health checks fail."
                    )
                    cursor.execute(
                        """
                        INSERT INTO chunks
                            (document_id, chunk_index, content, token_count, embedding)
                        VALUES (%s, %s, %s, %s, NULL)
                        ON CONFLICT (document_id, chunk_index) DO UPDATE
                        SET content = EXCLUDED.content,
                            token_count = EXCLUDED.token_count
                        """,
                        (document_id, chunk_index, content, 36),
                    )
                    inserted_chunks += 1

    return inserted_chunks


if __name__ == "__main__":
    print(f"Seeded {seed()} chunks")
