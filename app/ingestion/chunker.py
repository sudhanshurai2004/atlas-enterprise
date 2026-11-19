import hashlib
import tiktoken


ENCODING = tiktoken.get_encoding("cl100k_base")
CHUNK_TOKENS = 800
OVERLAP_TOKENS = 100


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def chunk_text(text: str) -> list[dict[str, object]]:
    token_ids = ENCODING.encode(text)
    chunks: list[dict[str, object]] = []
    seen_hashes: set[str] = set()
    start = 0

    while start < len(token_ids):
        end = min(start + CHUNK_TOKENS, len(token_ids))
        content = ENCODING.decode(token_ids[start:end]).strip()
        if content:
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                chunks.append(
                    {
                        "content": content,
                        "token_count": len(ENCODING.encode(content)),
                    }
                )
        if end == len(token_ids):
            break
        start = end - OVERLAP_TOKENS

    return chunks
