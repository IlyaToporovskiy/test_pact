import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator

import pytest
import requests


PACT_FILE = Path("pacts/frontend-app-user-provider-pact.json")


def _wait_until_healthy(base_url: str, timeout_seconds: int = 15) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"Provider did not become healthy at {base_url}")


@pytest.fixture(scope="module")
def provider_base_url() -> Iterator[str]:
    external_url = os.getenv("PROVIDER_BASE_URL")
    if external_url:
        _wait_until_healthy(external_url)
        yield external_url
        return

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
        ]
    )
    base_url = "http://127.0.0.1:8001"
    try:
        _wait_until_healthy(base_url)
        yield base_url
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_provider_honors_pact(provider_base_url: str) -> None:
    if not PACT_FILE.exists():
        pytest.fail(
            f"Pact file not found: {PACT_FILE}. "
            "Run consumer pact test first to generate contracts."
        )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pactman.verifier.command_line",
            "user-provider",
            provider_base_url,
            f"{provider_base_url}/_pact/provider_states",
            "--local-pact-file",
            str(PACT_FILE),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Pact verification failed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
