from pathlib import Path

import requests
from pactman import Consumer, Like, Provider


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACT_DIR = PROJECT_ROOT / "pacts"


def test_consumer_generates_pact() -> None:
    PACT_DIR.mkdir(parents=True, exist_ok=True)
    pact = Consumer("frontend-app").has_pact_with(
        Provider("user-provider"),
        pact_dir=str(PACT_DIR),
        host_name="127.0.0.1",
        port=1234,
    )

    (
        pact.given("a user with id 1 exists")
        .upon_receiving("a request for user 1")
        .with_request("get", "/users/1")
        .will_respond_with(
            200,
            body={
                "id": Like(1),
                "name": Like("Alice"),
                "email": Like("alice@example.com"),
            },
        )
    )

    (
        pact.given("user creation is available")
        .upon_receiving("a request to create a user")
        .with_request(
            "post",
            "/users",
            body={"name": "Bob", "email": "bob@example.com"},
            headers={"Content-Type": "application/json"},
        )
        .will_respond_with(
            201,
            body={
                "id": Like(2),
                "name": Like("Bob"),
                "email": Like("bob@example.com"),
            },
        )
    )

    pact.start_service()
    try:
        pact.setup()

        response_get = requests.get(f"{pact.uri}/users/1", timeout=5)
        assert response_get.status_code == 200
        assert response_get.json()["id"] == 1

        response_post = requests.post(
            f"{pact.uri}/users",
            json={"name": "Bob", "email": "bob@example.com"},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert response_post.status_code == 201
        assert response_post.json()["name"] == "Bob"

        pact.verify()
    finally:
        pact.stop_service()
