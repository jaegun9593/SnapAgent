"""
System template seeding on server startup.

Inserts 5 predefined system templates if they don't already exist (idempotent).
"""
import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Template

logger = logging.getLogger(__name__)

SYSTEM_TEMPLATES = [
    {
        "name": "RAG 문서 검색 Agent",
        "description": "업로드한 문서에서 벡터 유사도 검색으로 정확한 답변을 찾아주는 Agent",
        "category": "rag",
        "tool_config": [
            {"tool_type": "rag", "is_enabled": True, "sort_order": 1}
        ],
        "system_prompt_template": (
            "당신은 문서 기반 Q&A 전문 AI 어시스턴트입니다.\n"
            "사용자가 질문하면 RAG(Retrieval-Augmented Generation) 도구를 사용하여 "
            "업로드된 문서에서 관련 내용을 검색한 뒤, 검색 결과를 바탕으로 정확하고 근거 있는 답변을 제공하세요.\n\n"
            "규칙:\n"
            "1. 반드시 검색된 문서 내용을 근거로 답변하세요.\n"
            "2. 문서에 없는 내용은 추측하지 말고 '해당 문서에서 관련 내용을 찾을 수 없습니다'라고 안내하세요.\n"
            "3. 답변 시 출처(파일명, 페이지 등)를 함께 제시하세요.\n"
            "4. 한국어로 답변하세요."
        ),
    },
    {
        "name": "웹 검색 Agent",
        "description": "DuckDuckGo 웹 검색으로 최신 정보를 찾아주는 Agent",
        "category": "web_search",
        "tool_config": [
            {"tool_type": "web_search", "is_enabled": True, "sort_order": 1}
        ],
        "system_prompt_template": (
            "당신은 웹 검색 전문 AI 어시스턴트입니다.\n"
            "사용자가 질문하면 웹 검색 도구를 사용하여 최신 정보를 찾고, "
            "검색 결과를 종합하여 정확하고 유용한 답변을 제공하세요.\n\n"
            "규칙:\n"
            "1. 검색 결과를 기반으로 답변하되, 여러 소스를 종합하여 균형 있는 정보를 제공하세요.\n"
            "2. 정보의 출처(URL, 사이트명)를 가능한 한 함께 제시하세요.\n"
            "3. 최신 정보와 오래된 정보를 구분하여 안내하세요.\n"
            "4. 한국어로 답변하세요."
        ),
    },
    {
        "name": "하이브리드 Agent",
        "description": "문서 검색과 웹 검색을 결합하여 포괄적인 답변을 제공하는 Agent",
        "category": "hybrid",
        "tool_config": [
            {"tool_type": "rag", "is_enabled": True, "sort_order": 1},
            {"tool_type": "web_search", "is_enabled": True, "sort_order": 2},
        ],
        "system_prompt_template": (
            "당신은 내부 문서 검색과 웹 검색을 결합하여 포괄적인 답변을 제공하는 AI 어시스턴트입니다.\n"
            "사용자가 질문하면 먼저 업로드된 문서에서 관련 내용을 검색하고, "
            "필요한 경우 웹 검색을 통해 추가 정보를 수집하여 종합적인 답변을 제공하세요.\n\n"
            "규칙:\n"
            "1. 내부 문서의 정보를 우선시하되, 부족한 부분은 웹 검색으로 보완하세요.\n"
            "2. 내부 문서 출처와 웹 출처를 명확히 구분하여 표시하세요.\n"
            "3. 정보 간 충돌이 있으면 사용자에게 알리고, 내부 문서를 우선 기준으로 안내하세요.\n"
            "4. 한국어로 답변하세요."
        ),
    },
    {
        "name": "커스텀 API Agent",
        "description": "외부 REST API를 호출하여 실시간 데이터를 조회하는 Agent",
        "category": "custom",
        "tool_config": [
            {"tool_type": "custom_api", "is_enabled": True, "sort_order": 1}
        ],
        "system_prompt_template": (
            "당신은 외부 API 호출 전문 AI 어시스턴트입니다.\n"
            "사용자가 질문하면 등록된 커스텀 API를 호출하여 실시간 데이터를 조회하고, "
            "결과를 사용자가 이해하기 쉬운 형태로 가공하여 답변하세요.\n\n"
            "규칙:\n"
            "1. API 호출 결과를 사용자가 이해할 수 있도록 자연어로 변환하여 설명하세요.\n"
            "2. API 호출에 실패한 경우, 에러 내용을 사용자에게 친절하게 안내하세요.\n"
            "3. 민감한 정보(API 키, 인증 토큰 등)는 절대 노출하지 마세요.\n"
            "4. 한국어로 답변하세요."
        ),
    },
    {
        "name": "범용 대화 Agent",
        "description": "도구 없이 LLM만으로 일반 대화와 질의응답을 처리하는 Agent",
        "category": "general",
        "tool_config": [],
        "system_prompt_template": (
            "당신은 친절하고 유능한 범용 AI 어시스턴트입니다.\n"
            "사용자의 다양한 질문에 대해 정확하고 도움이 되는 답변을 제공하세요.\n\n"
            "규칙:\n"
            "1. 사용자의 질문 의도를 정확히 파악하여 맞춤형 답변을 제공하세요.\n"
            "2. 확실하지 않은 정보는 그 사실을 명시하세요.\n"
            "3. 복잡한 주제는 단계별로 나누어 설명하세요.\n"
            "4. 한국어로 답변하세요."
        ),
    },
]


async def seed_system_templates(db: AsyncSession) -> None:
    """
    Seed system templates into the database.

    Idempotent: skips templates that already exist (matched by name).
    """
    # Get existing system template names
    result = await db.execute(
        select(Template.name).where(
            Template.is_system == True,
            Template.use_yn == "Y",
        )
    )
    existing_names: List[str] = [row[0] for row in result.all()]

    seeded_count = 0
    for tmpl_data in SYSTEM_TEMPLATES:
        if tmpl_data["name"] in existing_names:
            logger.debug("System template already exists, skipping: %s", tmpl_data["name"])
            continue

        template = Template(
            name=tmpl_data["name"],
            description=tmpl_data["description"],
            category=tmpl_data["category"],
            tool_config=tmpl_data["tool_config"],
            system_prompt_template=tmpl_data["system_prompt_template"],
            is_system=True,
            created_by="system",
        )
        db.add(template)
        seeded_count += 1

    if seeded_count > 0:
        await db.commit()
        logger.info("Seeded %d system templates", seeded_count)
    else:
        logger.info("All system templates already exist, nothing to seed")
