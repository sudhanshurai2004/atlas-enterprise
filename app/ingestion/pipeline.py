import argparse
import os
import shutil
import tempfile
from pathlib import Path

import psycopg
from google.cloud import storage
from pypdf import PdfReader

from app.config import settings
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_texts


def _read_text_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def _local_sources(source_dir: Path) -> list[tuple[str, str, str]]:
    sources: list[tuple[str, str, str]] = []
    for path in sorted(source_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in (".txt", ".pdf", ".md"):
            sources.append(
                (
                    str(path),
                    path.stem,
                    path.suffix.lower().lstrip("."),
                )
            )
    return sources


def _gcs_sources(bucket_name: str) -> list[tuple[str, str, str]]:
    client = storage.Client(project=settings.gcp_project_id)
    bucket = client.bucket(bucket_name)
    sources: list[tuple[str, str, str]] = []
    temp_path = Path(tempfile.mkdtemp(prefix="atlas-gcs-"))

    for blob in bucket.list_blobs():
        suffix = Path(blob.name).suffix.lower()
        if suffix not in (".txt", ".pdf", ".md"):
            continue
        local_path = temp_path / Path(blob.name).name
        blob.download_to_filename(str(local_path))
        sources.append(
            (
                str(local_path),
                Path(blob.name).stem,
                suffix.lstrip("."),
            )
        )

    return sources


def run_ingestion(source_dir: str | None = None) -> tuple[int, int]:
    bucket_name = os.getenv("GCS_BUCKET") or settings.gcs_bucket
    sources = (
        _gcs_sources(bucket_name)
        if bucket_name
        else _local_sources(Path(source_dir or "data"))
    )

    document_count = 0
    chunk_count = 0
    gcs_download_root: Path | None = None
    if bucket_name and sources:
        gcs_download_root = Path(sources[0][0]).parent

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            for uri, title, suffix in sources:
                path = Path(uri)
                content = _read_text_file(path)
                if not content.strip():
                    continue

                source_type = "pdf" if suffix == "pdf" else "wiki"
                gcs_uri = (
                    f"gs://{bucket_name}/{path.name}"
                    if bucket_name
                    else f"local://{path.as_posix()}"
                )

                cursor.execute(
                    """
                    INSERT INTO documents (source_type, gcs_uri, title, metadata)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (gcs_uri) DO UPDATE
                    SET title = EXCLUDED.title,
                        source_type = EXCLUDED.source_type,
                        metadata = EXCLUDED.metadata
                    RETURNING id
                    """,
                    (source_type, gcs_uri, title, '{"ingestion": true}'),
                )
                document_id = cursor.fetchone()[0]
                document_count += 1

                chunks = chunk_text(content)
                texts = [str(chunk["content"]) for chunk in chunks]
                embeddings = embed_texts(texts, "RETRIEVAL_DOCUMENT")

                for chunk_index, (chunk, embedding) in enumerate(
                    zip(chunks, embeddings)
                ):
                    cursor.execute(
                        """
                        INSERT INTO chunks
                            (document_id, chunk_index, content, token_count, embedding)
                        VALUES (%s, %s, %s, %s, %s::vector)
                        ON CONFLICT (document_id, chunk_index) DO UPDATE
                        SET content = EXCLUDED.content,
                            token_count = EXCLUDED.token_count,
                            embedding = EXCLUDED.embedding
                        """,
                        (
                            document_id,
                            chunk_index,
                            chunk["content"],
                            chunk["token_count"],
                            str(embedding),
                        ),
                    )
                    chunk_count += 1

    if gcs_download_root:
        shutil.rmtree(gcs_download_root, ignore_errors=True)

    return document_count, chunk_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data")
    args = parser.parse_args()
    ingested_documents, ingested_chunks = run_ingestion(args.source)
    print(
        f"Ingested {ingested_documents} docs, "
        f"{ingested_chunks} chunks"
    )
