"""
Test fixtures for SnapAgent backend API tests.

Uses httpx AsyncClient with the real FastAPI app.
CaptchaService.verify is mocked to always return True.
"""
import asyncio
import os
from typing import Dict
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"

from app.main import app  # noqa: E402

BASE_URL = "http://test"
API = "/api/v1"

# Test user credentials (KISA-compliant password: 3종 이상 8자+)
TEST_EMAIL = "testuser@snapagent.dev"
TEST_PASSWORD = "Snap!9xKw"  # upper + lower + special + digit = 4종, 9자
TEST_FULL_NAME = "Test User"

# Mark all tests in session scope so they share one event loop
pytestmark = pytest.mark.asyncio(scope="session")


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy."""
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(scope="session")
async def client():
    """Async HTTP client bound to the FastAPI app (session-scoped)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def auth_headers(client: AsyncClient) -> Dict[str, str]:
    """Register a test user and return Authorization headers.

    CaptchaService.verify is patched to always return True.
    """
    # Try to register first
    with patch("app.api.v1.auth.CaptchaService.verify", return_value=True):
        resp = await client.post(
            f"{API}/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": TEST_FULL_NAME,
                "captcha_id": "test-captcha-id",
                "captcha_text": "AAAAAA",
            },
        )

    if resp.status_code == 201:
        token = resp.json()["access_token"]
    else:
        # User already exists — login instead
        resp = await client.post(
            f"{API}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        token = resp.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
