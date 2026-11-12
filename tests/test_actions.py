from config.actions import contains_dangerous_sql


def test_blocks_dangerous_sql_keywords() -> None:
    assert contains_dangerous_sql("DROP TABLE customers")
    assert contains_dangerous_sql("delete from customers")
    assert contains_dangerous_sql("TRUNCATE TABLE customers")


def test_allows_unrelated_text() -> None:
    assert not contains_dangerous_sql("SELECT * FROM customers")
    assert not contains_dangerous_sql("Как удалить таблицу customers?")
