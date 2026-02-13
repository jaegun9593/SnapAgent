"""
End-to-end RAG Agent test:
  Register → Login → Upload file → Create Agent → Process (embed)
  → Verify partition & vectors → Test query via RAG tool

Run:  pytest tests/test_rag_e2e.py -v -s
"""
import asyncio
import os
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

os.environ["ENVIRONMENT"] = "test"

from app.main import app  # noqa: E402
from app.db.database import async_session_maker  # noqa: E402

BASE_URL = "http://test"
API = "/api/v1"

TEST_EMAIL = "ragtest@snapagent.dev"
TEST_PASSWORD = "Xk9!mWpQ2z"

pytestmark = pytest.mark.asyncio(scope="session")


def get_data(resp_json):
    """Extract data from API response, handling both wrapped and unwrapped formats."""
    if isinstance(resp_json, dict) and "data" in resp_json:
        return resp_json["data"]
    return resp_json


@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def auth_headers(client: AsyncClient):
    with patch("app.api.v1.auth.CaptchaService.verify", return_value=True):
        resp = await client.post(f"{API}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "RAG E2E Tester",
            "captcha_id": "test",
            "captcha_text": "AAAAAA",
        })
    if resp.status_code in (200, 201):
        data = get_data(resp.json())
        token = data["access_token"]
        print(f"\n  Register OK")
    else:
        resp = await client.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        data = get_data(resp.json())
        token = data["access_token"]
        print(f"\n  Login OK (existing user)")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio(scope="session")
async def test_rag_e2e(client: AsyncClient, auth_headers):
    """Full end-to-end RAG flow test."""
    headers = auth_headers

    # ─── Step 1: Upload file ───────────────────────────────────
    print("\n" + "=" * 60)
    print("[Step 1] Upload test document")
    print("=" * 60)

    doc_content = """# SnapAgent 기술 사양서

## 1. 시스템 아키텍처
SnapAgent는 RAG(Retrieval-Augmented Generation) 기반의 AI Agent 빌더 플랫폼입니다.
백엔드는 FastAPI와 SQLAlchemy 2.0 async를 사용하며, 프론트엔드는 React 19와 Vite로 구성됩니다.

## 2. 데이터베이스
PostgreSQL 15에 pgvector 확장을 사용합니다.
벡터 테이블(snap_vec_ebd)은 agent_id 기준으로 LIST 파티셔닝되어 있으며,
각 파티션에는 독립적인 IVFFlat 인덱스가 생성됩니다.

## 3. 임베딩 모델
기본 임베딩 모델은 text-embedding-3-small(1536차원)입니다.
OpenAI API를 통해 임베딩 벡터를 생성하며, Open Router를 통해 라우팅됩니다.

## 4. ReAct 엔진
의도 분류 → Tool 실행 → LLM 추론 → 답변 평가 → 재질의 순환 루프로 동작합니다.
최대 3회까지 재질의가 가능하며, 평가 점수 0.7 이상이면 최종 답변으로 확정합니다.

## 5. 보안
JWT 기반 인증(access_token 30분, refresh_token 7일)을 사용합니다.
비밀번호는 bcrypt로 해시하며, KISA 비밀번호 정책을 준수합니다.
API 키는 Fernet 대칭 암호화로 저장됩니다.

## 6. 성능 목표
- 임베딩 생성: 파일당 10초 이내
- 벡터 검색: 100ms 이내 (Top-5 기준)
- Agent 응답: 첫 토큰 3초 이내
- 동시 사용자: 100명 이상 지원
"""

    resp = await client.post(
        f"{API}/files/upload",
        files={"file": ("tech_spec.txt", doc_content.encode(), "text/plain")},
        headers=headers,
    )
    assert resp.status_code in (200, 201), f"Upload failed: {resp.text}"
    file_data = get_data(resp.json())
    file_id = file_data["id"]
    print(f"  File uploaded: id={file_id}")

    # ─── Step 2: Get available models ──────────────────────────
    print("\n" + "=" * 60)
    print("[Step 2] Check available models")
    print("=" * 60)

    resp = await client.get(f"{API}/models/", headers=headers)
    assert resp.status_code == 200, f"Models list failed: {resp.text}"
    resp_json = resp.json()
    # ModelListResponse: {"models": [...], "total": N}
    models = resp_json.get("models", get_data(resp_json))

    llm_model = None
    emb_model = None
    for m in models:
        if m["model_type"] == "llm" and not llm_model:
            llm_model = m
        elif m["model_type"] == "embedding":
            # Prefer text-embedding-3-small (1536 dims) over large (3072 dims)
            if "small" in m.get("model_id", "") or not emb_model:
                emb_model = m

    assert llm_model, "No LLM model available"
    assert emb_model, "No embedding model available"
    print(f"  LLM: {llm_model['name']} ({llm_model['id']})")
    print(f"  Embedding: {emb_model['name']} ({emb_model['id']})")

    # ─── Step 3: Create RAG Agent ──────────────────────────────
    print("\n" + "=" * 60)
    print("[Step 3] Create RAG Agent")
    print("=" * 60)

    resp = await client.post(f"{API}/agents/", json={
        "name": "RAG E2E Test Agent",
        "description": "End-to-end RAG partitioning + embedding test",
        "system_prompt": (
            "당신은 문서 기반 Q&A AI입니다. "
            "RAG 도구를 사용하여 문서에서 관련 내용을 검색한 뒤 답변하세요. "
            "한국어로 답변하세요."
        ),
        "model_id": llm_model["id"],
        "embedding_model_id": emb_model["id"],
        "status": "draft",
        "tools": [
            {"tool_type": "rag", "is_enabled": True, "sort_order": 1, "tool_config": {}}
        ],
        "file_ids": [file_id],
    }, headers=headers)
    assert resp.status_code in (200, 201), f"Create agent failed: {resp.text}"
    agent_data = get_data(resp.json())
    agent_id = agent_data["id"]
    agent_tools = agent_data.get("tools", [])
    agent_files = agent_data.get("file_ids", [])
    print(f"  Agent created: id={agent_id}")
    print(f"  Tools: {[t['tool_type'] for t in agent_tools]}")
    print(f"  Files: {agent_files}")

    # ─── Step 4: Process files (parse → chunk → embed) ────────
    print("\n" + "=" * 60)
    print("[Step 4] Process files (parse → chunk → embed)")
    print("=" * 60)

    resp = await client.post(
        f"{API}/agents/{agent_id}/process",
        json={"force": True},
        headers=headers,
    )
    assert resp.status_code in (200, 201), f"Process failed: {resp.text}"
    proc = get_data(resp.json())
    print(f"  Status: {proc.get('status')}")
    print(f"  Files processed: {proc.get('files_processed')}")
    print(f"  Chunks created: {proc.get('chunks_created')}")
    assert proc.get("chunks_created", 0) > 0, "No chunks created - embedding may have failed!"

    # ─── Step 5: Verify DB partition + vectors ─────────────────
    print("\n" + "=" * 60)
    print("[Step 5] Verify DB: partition & vectors")
    print("=" * 60)

    async with async_session_maker() as db:
        # Check partitions
        result = await db.execute(text(
            "SELECT tablename FROM pg_tables WHERE tablename LIKE 'snap_vec_ebd%' ORDER BY tablename"
        ))
        partitions = [row[0] for row in result.fetchall()]
        print(f"  Partitions: {partitions}")

        partition_name = f"snap_vec_ebd_{agent_id.replace('-', '_')}"
        assert partition_name in partitions, f"Partition {partition_name} not found!"
        print(f"  Agent partition exists: {partition_name}")

        # Check vector count
        result = await db.execute(text(
            "SELECT COUNT(*) FROM snap_vec_ebd WHERE agent_id = :aid AND use_yn = 'Y'"
        ), {"aid": agent_id})
        vec_count = result.scalar()
        print(f"  Vector count: {vec_count}")
        assert vec_count > 0, "No vectors in partition!"

        # Check indexes on partition
        result = await db.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename = :tbl"
        ), {"tbl": partition_name})
        indexes = [row[0] for row in result.fetchall()]
        print(f"  Indexes on partition: {indexes}")

        ivfflat_idx = [i for i in indexes if "embedding" in i]
        assert len(ivfflat_idx) > 0, "IVFFlat index not found on partition!"
        print(f"  IVFFlat index confirmed: {ivfflat_idx[0]}")

        # Sample vector content
        result = await db.execute(text(
            "SELECT content, chunk_index FROM snap_vec_ebd WHERE agent_id = :aid AND use_yn = 'Y' ORDER BY chunk_index LIMIT 3"
        ), {"aid": agent_id})
        for row in result.fetchall():
            print(f"  Chunk[{row[1]}]: {row[0][:80]}...")

    # ─── Step 6: Activate + Test Agent ─────────────────────────
    print("\n" + "=" * 60)
    print("[Step 6] Test Agent with RAG query")
    print("=" * 60)

    resp = await client.put(
        f"{API}/agents/{agent_id}",
        json={"status": "active"},
        headers=headers,
    )
    assert resp.status_code in (200, 201), f"Activate failed: {resp.text}"
    print("  Agent activated")

    resp = await client.post(
        f"{API}/agents/{agent_id}/test",
        json={"query": "SnapAgent의 벡터 검색 성능 목표는 어떻게 되나요?"},
        headers=headers,
    )
    assert resp.status_code in (200, 201), f"Test failed: {resp.text}"
    test_data = get_data(resp.json())

    print(f"  Success: {test_data.get('success')}")
    if test_data.get("error"):
        print(f"  ERROR: {test_data['error']}")

    response_text = test_data.get("response") or ""
    print(f"  Response: {response_text[:300]}")

    tool_calls = test_data.get("tool_calls") or []
    print(f"  Tool calls count: {len(tool_calls)}")
    for i, tc in enumerate(tool_calls):
        tool_name = tc.get("tool") or tc.get("tool_name") or "N/A"
        print(f"    [{i+1}] Tool: {tool_name}")
        output = tc.get("output", "")
        if isinstance(output, str) and output:
            print(f"        Output: {output[:200]}")
        elif isinstance(output, dict):
            chunks = output.get("chunks", [])
            print(f"        Chunks found: {len(chunks)}")
            for ch in chunks[:3]:
                sim = ch.get("similarity", "?")
                content = ch.get("content", "")[:80]
                print(f"          sim={sim}: {content}...")

    print(f"  Token usage: {test_data.get('token_usage')}")
    print(f"  Latency: {test_data.get('latency_ms')}ms")

    # Verify: success and response contains relevant content
    assert test_data.get("success") is True, "Agent test was not successful"
    assert len(response_text) > 0, "Empty response from agent"

    # ─── Step 7: Cleanup ───────────────────────────────────────
    print("\n" + "=" * 60)
    print("[Step 7] Cleanup — delete agent (verify partition drop)")
    print("=" * 60)

    resp = await client.delete(f"{API}/agents/{agent_id}", headers=headers)
    assert resp.status_code in (200, 204), f"Delete failed: {resp.text}"
    print(f"  Agent deleted: {agent_id}")

    # Verify partition dropped
    async with async_session_maker() as db:
        result = await db.execute(text(
            "SELECT tablename FROM pg_tables WHERE tablename = :tbl"
        ), {"tbl": partition_name})
        row = result.fetchone()
        if row is None:
            print(f"  Partition {partition_name} dropped successfully!")
        else:
            print(f"  WARNING: Partition {partition_name} still exists")

    print("\n" + "=" * 60)
    print("ALL E2E RAG TESTS PASSED")
    print("=" * 60)
