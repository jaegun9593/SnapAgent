"""
SnapAgent Backend API integration tests.

These tests run against the real database inside Docker.
All tests share one event loop (session-scoped) so the DB engine stays valid.
"""
import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from tests.conftest import API, TEST_EMAIL, TEST_PASSWORD

# All async tests in this module share one session-scoped event loop
pytestmark = pytest.mark.asyncio(scope="session")

# ---------------------------------------------------------------------------
# Module-scoped state shared across ordered tests
# ---------------------------------------------------------------------------
_state: dict = {}


# =========================================================================
# 1. Health check
# =========================================================================
async def test_health_check(client: AsyncClient):
    """GET / should return 200 with status 'running'."""
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "running"


# =========================================================================
# 2. CAPTCHA 생성
# =========================================================================
async def test_captcha_generate(client: AsyncClient):
    """GET /auth/captcha should return captcha_id and image_base64."""
    resp = await client.get(f"{API}/auth/captcha")
    assert resp.status_code == 200
    body = resp.json()
    assert "captcha_id" in body
    assert body["image_base64"].startswith("data:image/png;base64,")


# =========================================================================
# 3. 회원가입 (auth_headers fixture handles this, but explicit test too)
# =========================================================================
async def test_register(client: AsyncClient, auth_headers: dict):
    """POST /auth/register — already executed by fixture; verify headers exist."""
    assert "Authorization" in auth_headers
    assert auth_headers["Authorization"].startswith("Bearer ")


# =========================================================================
# 4. 로그인
# =========================================================================
async def test_login(client: AsyncClient, auth_headers: dict):
    """POST /auth/login should return access_token + refresh_token."""
    # auth_headers fixture ensures the test user is already registered
    resp = await client.post(
        f"{API}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


# =========================================================================
# 5. 토큰 갱신
# =========================================================================
async def test_token_refresh(client: AsyncClient, auth_headers: dict):
    """POST /auth/refresh should return new tokens."""
    # Login to get a fresh refresh token in this event loop
    login_resp = await client.post(
        f"{API}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    refresh = login_resp.json()["refresh_token"]

    resp = await client.post(
        f"{API}/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body


# =========================================================================
# 6. 내 정보 조회
# =========================================================================
async def test_get_me(client: AsyncClient, auth_headers: dict):
    """GET /users/me should return the test user's profile."""
    resp = await client.get(f"{API}/users/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == TEST_EMAIL


# =========================================================================
# 7. 템플릿 목록 (시스템 5종)
# =========================================================================
async def test_list_templates(client: AsyncClient, auth_headers: dict):
    """GET /templates/ should return at least 5 system templates."""
    resp = await client.get(f"{API}/templates/", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 5
    categories = {t["category"] for t in body["templates"]}
    assert {"rag", "web_search", "hybrid", "custom", "general"}.issubset(categories)


# =========================================================================
# 8. 템플릿 생성 거부 (일반 사용자 → 403)
# =========================================================================
async def test_create_template_forbidden(client: AsyncClient, auth_headers: dict):
    """POST /templates/ by a regular user should be 403 Forbidden."""
    resp = await client.post(
        f"{API}/templates/",
        headers=auth_headers,
        json={
            "name": "Illegal Template",
            "description": "Should fail",
            "category": "general",
        },
    )
    assert resp.status_code == 403


# =========================================================================
# 9. 파일 업로드
# =========================================================================
async def test_file_upload(client: AsyncClient, auth_headers: dict):
    """POST /files/upload should accept a text file."""
    content = b"Hello SnapAgent test file content."
    resp = await client.post(
        f"{API}/files/upload",
        headers=auth_headers,
        files={"file": ("test_doc.txt", io.BytesIO(content), "text/plain")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["filename"] == "test_doc.txt"
    _state["file_id"] = body["id"]


# =========================================================================
# 10. 파일 목록
# =========================================================================
async def test_list_files(client: AsyncClient, auth_headers: dict):
    """GET /files/ should include the uploaded file."""
    # Upload a file first to ensure at least one exists
    content = b"Test file for listing."
    await client.post(
        f"{API}/files/upload",
        headers=auth_headers,
        files={"file": ("list_test.txt", io.BytesIO(content), "text/plain")},
    )

    resp = await client.get(f"{API}/files/", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1


# =========================================================================
# 11. Agent 생성
# =========================================================================
async def test_create_agent(client: AsyncClient, auth_headers: dict):
    """POST /agents should create a new agent."""
    resp = await client.post(
        f"{API}/agents/",
        headers=auth_headers,
        json={
            "name": "Test Agent",
            "description": "Integration test agent",
            "system_prompt": "You are a test assistant.",
            "status": "draft",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Test Agent"
    _state["agent_id"] = body["id"]


# =========================================================================
# 12. Agent 목록
# =========================================================================
async def test_list_agents(client: AsyncClient, auth_headers: dict):
    """GET /agents should include the created agent."""
    # Create an agent first to ensure at least one exists
    await client.post(
        f"{API}/agents/",
        headers=auth_headers,
        json={"name": "List Test Agent", "status": "draft"},
    )

    resp = await client.get(f"{API}/agents/", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1


# =========================================================================
# 13. Agent 상세
# =========================================================================
async def test_get_agent(client: AsyncClient, auth_headers: dict):
    """GET /agents/{id} should return agent details."""
    # Create an agent first
    create_resp = await client.post(
        f"{API}/agents/",
        headers=auth_headers,
        json={"name": "Detail Test Agent", "status": "draft"},
    )
    agent_id = create_resp.json()["id"]

    resp = await client.get(f"{API}/agents/{agent_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == agent_id
    assert body["name"] == "Detail Test Agent"


# =========================================================================
# 14. Agent 삭제
# =========================================================================
async def test_delete_agent(client: AsyncClient, auth_headers: dict):
    """DELETE /agents/{id} should soft-delete the agent."""
    # Create an agent to delete
    create_resp = await client.post(
        f"{API}/agents/",
        headers=auth_headers,
        json={"name": "Delete Test Agent", "status": "draft"},
    )
    agent_id = create_resp.json()["id"]

    resp = await client.delete(f"{API}/agents/{agent_id}", headers=auth_headers)
    assert resp.status_code == 200

    # Verify it no longer appears in the list
    resp2 = await client.get(f"{API}/agents/{agent_id}", headers=auth_headers)
    assert resp2.status_code == 404


# =========================================================================
# 15. 채팅 세션 생성
# =========================================================================
async def test_create_chat_session(client: AsyncClient, auth_headers: dict):
    """POST /chat/sessions should create a session for an agent."""
    # Create a fresh agent for chat testing
    agent_resp = await client.post(
        f"{API}/agents/",
        headers=auth_headers,
        json={"name": "Chat Test Agent", "status": "active"},
    )
    assert agent_resp.status_code == 201
    agent_id = agent_resp.json()["id"]

    resp = await client.post(
        f"{API}/chat/sessions",
        headers=auth_headers,
        json={"agent_id": agent_id, "title": "Test Session"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["agent_id"] == agent_id
    assert body["title"] == "Test Session"
    _state["session_id"] = body["id"]
    _state["chat_agent_id"] = agent_id


# =========================================================================
# 16. 채팅 세션 목록
# =========================================================================
async def test_list_chat_sessions(client: AsyncClient, auth_headers: dict):
    """GET /chat/sessions should include the created session."""
    # Create agent + session to ensure at least one exists
    agent_resp = await client.post(
        f"{API}/agents/",
        headers=auth_headers,
        json={"name": "Session List Agent", "status": "active"},
    )
    agent_id = agent_resp.json()["id"]

    await client.post(
        f"{API}/chat/sessions",
        headers=auth_headers,
        json={"agent_id": agent_id, "title": "List Test Session"},
    )

    resp = await client.get(f"{API}/chat/sessions", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
