from fastapi.testclient import TestClient

from app import app, rails


def test_dangerous_sql_is_blocked_without_calling_llm() -> None:
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "DROP TABLE customers;"}
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {"reply": "Запрос заблокирован политикой."}
    assert len(rails.explain().llm_calls) == 0
