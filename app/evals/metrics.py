import os


def start_span(name: str, attributes: dict[str, object] | None = None):
    """Return a lightweight local span placeholder until Langfuse credentials exist."""
    return {
        "name": name,
        "attributes": attributes or {},
        "langfuse_enabled": bool(
            os.getenv("LANGFUSE_PUBLIC_KEY")
            and os.getenv("LANGFUSE_SECRET_KEY")
        ),
    }
