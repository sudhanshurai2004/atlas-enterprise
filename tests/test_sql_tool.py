from app.tools.sql_tool import validate_select


def test_valid_select() -> None:
    valid, message = validate_select(
        "SELECT name, plan FROM billing_customers "
        "WHERE plan = 'pro';"
    )

    assert valid is True
    assert message == "valid"


def test_mutation_rejected() -> None:
    valid, message = validate_select("DROP TABLE chunks")

    assert valid is False
    assert "SELECT" in message


def test_table_allowlist_rejected() -> None:
    valid, message = validate_select("SELECT * FROM chunks")

    assert valid is False
    assert "allowlist" in message


def test_multiple_statements_rejected() -> None:
    valid, message = validate_select(
        "SELECT * FROM billing_customers; DROP TABLE chunks"
    )

    assert valid is False
