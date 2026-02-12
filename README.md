# SnapAgent - RAG Agent Builder

사용자가 RAG, 웹검색, 도구사용 기반의 AI Agent를 직접 생성하고 운영할 수 있는 플랫폼.
모든 Agent는 **ReAct(Reasoning + Acting)** 패턴으로 동작하며, 의도 분류 → Tool 실행 → 답변 평가 → 재질의 순환 루프를 포함한다.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React 19, Vite, TypeScript, Zustand, React Query, Tailwind CSS, shadcn/ui, Recharts |
| Admin Frontend | 동일 스택 (별도 repo: [SnapAgentAdmin](https://github.com/jaegun9593/SnapAgentAdmin.git)) |
| Backend | FastAPI, Python 3.12+, SQLAlchemy 2.0 (async), LangChain, LangGraph |
| Database | PostgreSQL 15+ with pgvector |
| Auth | JWT (python-jose + bcrypt) |
| LLM Router | Open Router API |
| Infra | Docker, Docker Compose |

---

## 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- Node.js 18+
- Python 3.12+

### 로컬 개발환경 실행

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일에서 OPENROUTER_API_KEY 등 설정

# 2. 원클릭 시작 (DB Docker + 호스트 backend/frontend)
./scripts/local-start.sh

# 또는 수동 실행
docker-compose -f docker-compose.local.yml up -d   # DB 시작
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
cd frontend && npm run dev
```

### Docker 개발환경 실행

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 포트 구성

| 서비스 | 개발 포트 | 운영 포트 |
|--------|-----------|-----------|
| Database (PostgreSQL) | 5433 | 5433 |
| Backend (FastAPI) | 8001 | 8001 |
| Frontend (SnapAgent) | 5174 | 3001 |
| Admin (SnapAgentAdmin) | 5175 | 3002 |

---

## 프로젝트 구조

```
SnapAgent/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI 엔트리포인트 + lifespan (템플릿 시드)
│   │   ├── config.py                  # Pydantic Settings
│   │   ├── api/
│   │   │   ├── deps.py               # 의존성 주입 (CurrentUser, AdminUser, DBSession)
│   │   │   └── v1/
│   │   │       ├── auth.py            # 회원가입/로그인/토큰갱신
│   │   │       ├── users.py           # 사용자 관리
│   │   │       ├── agents.py          # Agent CRUD + 테스트 + RAG 처리
│   │   │       ├── templates.py       # 템플릿 (GET: 사용자, POST/PUT/DELETE: 관리자)
│   │   │       ├── files.py           # 파일 업로드/관리
│   │   │       ├── chat.py            # SSE 스트리밍 채팅
│   │   │       ├── dashboard.py       # 사용자 대시보드
│   │   │       └── admin/             # 관리자 전용 API
│   │   ├── services/
│   │   │   ├── template_seed.py       # 서버 시작 시 시스템 템플릿 5종 자동 시드
│   │   │   └── ...                    # auth, agent, file, chat 등
│   │   ├── agent/                     # ReAct Agent 엔진
│   │   │   ├── react_agent.py         # ReAct 루프
│   │   │   ├── intent_classifier.py   # 의도 분류
│   │   │   ├── tool_executor.py       # Tool 실행
│   │   │   ├── evaluator.py           # 답변 평가
│   │   │   └── tools/                 # RAG, 웹검색, 커스텀 API
│   │   ├── rag/                       # RAG 파이프라인
│   │   │   ├── parsing.py             # 문서 파싱
│   │   │   ├── chunking.py            # 텍스트 청킹
│   │   │   ├── embedding.py           # 임베딩 생성 + 전체 처리 오케스트레이션
│   │   │   ├── vectorstore.py         # pgvector 저장/검색
│   │   │   ├── retriever.py           # 시맨틱 검색
│   │   │   └── ocr.py                 # OCR (Tesseract, 한/영)
│   │   ├── db/
│   │   │   ├── base.py                # Base + AuditMixin
│   │   │   ├── database.py            # AsyncSession 설정
│   │   │   └── models.py              # ORM 모델 (Mapped 스타일, Relationship 없음)
│   │   ├── schemas/                   # Pydantic DTO
│   │   └── core/                      # JWT, 암호화, 예외
│   └── sql/                           # DB 초기화 SQL (13개 테이블)
│
├── frontend/
│   ├── src/
│   │   ├── pages/                     # 로그인, 회원가입, Agent 목록/생성/채팅, 템플릿, 대시보드
│   │   ├── components/
│   │   │   ├── layout/                # Header (마이페이지/로그아웃 버튼), Sidebar, MainLayout
│   │   │   ├── agent/                 # AgentCard, 생성 위자드 (5단계 스텝)
│   │   │   ├── chat/                  # ChatPanel, ToolExecutionLayer (접이식)
│   │   │   ├── template/              # TemplateCard (읽기 전용)
│   │   │   └── dashboard/             # 사용량 차트, 비용 추정
│   │   ├── hooks/                     # React Query 커스텀 훅
│   │   ├── services/                  # Axios API 서비스
│   │   ├── stores/                    # Zustand (authStore)
│   │   └── lib/                       # Axios 인터셉터, React Query 설정
│   └── ...
│
├── docker-compose.local.yml           # 로컬 (DB만 Docker)
├── docker-compose.dev.yml             # 개발 (전체 Docker)
├── docker-compose.prd.yml             # 운영
└── scripts/
    ├── local-start.sh
    └── local-stop.sh
```

---

## 핵심 기능

### 1. Agent 생성 위자드 (5단계)

| 단계 | 설명 |
|------|------|
| BasicInfoStep | Agent 이름, 설명, 시스템 프롬프트 입력 |
| FileUploadStep | RAG용 문서 파일 업로드 |
| ToolSelectStep | 사용할 Tool 선택 (RAG, 웹검색, 커스텀 API) |
| ModelSelectStep | LLM/임베딩 모델 선택 (관리자가 등록한 Open Router 모델) |
| TestStep | Agent 테스트 실행 |

### 2. ReAct Agent 엔진

```
사용자 질문
    ↓
[1] 의도 분류 (Intent Classifier)
    - RAG 검색 / 웹 검색 / 일반 대화 / 복합 판단
    ↓
[2] Tool 선택 & 실행 (Tool Executor)
    - RAG Tool → 벡터 검색 → 관련 문서 추출
    - Web Search Tool → DuckDuckGo 검색
    - Custom API Tool → 외부 REST API 호출
    ↓
[3] LLM 추론 (LangChain)
    - 시스템 프롬프트 + Tool 결과 + 사용자 질문 → 스트리밍 응답 (SSE)
    ↓
[4] 답변 평가 (Evaluator)
    - 충분 → 최종 답변 반환
    - 불충분 → [2]로 재질의 (최대 3회)
```

### 3. RAG 파이프라인

Agent 생성 후 `POST /api/v1/agents/{id}/process` 호출 시 자동 처리:

```
파일 → 파싱 → 청킹 → 임베딩 → 벡터 저장 (pgvector)
```

#### 파싱 (parsing.py)

| 파일 형식 | 라이브러리 | 방식 |
|-----------|-----------|------|
| PDF | pypdf | 전체 페이지 텍스트 추출 |
| DOCX | python-docx | 문단별 텍스트 추출 |
| TXT / MD | aiofiles | 비동기 파일 읽기 |
| CSV | pandas | DataFrame → string 변환 |
| XLSX | pandas | Excel reader → string 변환 |
| 이미지 | pytesseract + PIL | Tesseract OCR (한/영) |

#### 청킹 (chunking.py)

- **방식**: Recursive Character Splitting
- **기본 설정**: chunk_size=1000자, chunk_overlap=200자
- **분할 우선순위**: `"\n\n"` → `"\n"` → `". "` → `" "` → 문자 단위
- Agent별 config로 커스터마이징 가능

#### 임베딩 (embedding.py)

- **API**: Open Router (httpx 비동기 호출, 30초 타임아웃)
- **기본 모델**: `text-embedding-3-small`
- Agent에 `embedding_model_id` 설정 시 해당 모델로 오버라이드
- 청크별 개별 임베딩, 실패 시 해당 청크 스킵 후 계속 진행

#### 벡터 저장/검색 (vectorstore.py, retriever.py)

- **테이블**: `snap_vec_ebd` (agent_id 기반 LIST 파티셔닝)
- **인덱스**: IVFFlat (코사인 유사도)
- **검색**: pgvector `<=>` 연산자, `similarity = 1 - distance`
- **기본값**: top_k=5, threshold=0.3

### 4. SSE 스트리밍 채팅

각 단계별 이벤트를 SSE로 실시간 스트리밍:

```
event: thinking        # 의도 분류 결과
event: tool_start      # Tool 실행 시작
event: tool_result     # Tool 실행 결과
event: evaluation      # 답변 평가 점수
event: answer_token    # LLM 응답 토큰 (스트리밍)
event: done            # 완료
```

프론트엔드에서는 **Claude 스타일 접이식 레이어**(ToolExecutionLayer)로 표시:
- 접힌 상태: Tool명 + 소요시간 + 상태
- 펼친 상태: 입력값, 출력값, 검색 소스, 스코어 등 상세 정보

### 5. 시스템 템플릿 (관리자 전용)

서버 기동 시 5종 시스템 템플릿이 자동 시드 (멱등성 보장):

| 템플릿 | 카테고리 | Tool | 설명 |
|--------|---------|------|------|
| RAG 문서 검색 Agent | `rag` | RAG | 업로드 문서에서 벡터 유사도 검색 |
| 웹 검색 Agent | `web_search` | Web Search | DuckDuckGo 웹 검색으로 최신 정보 |
| 하이브리드 Agent | `hybrid` | RAG + Web Search | 문서 검색 + 웹 검색 결합 |
| 커스텀 API Agent | `custom` | Custom API | 외부 REST API 호출 |
| 범용 대화 Agent | `general` | 없음 | LLM만으로 일반 대화 |

- 템플릿 생성/수정/삭제는 **관리자(AdminUser)만 가능**
- 사용자는 템플릿 목록 조회 후 선택하여 Agent 생성

---

## API 엔드포인트

### 인증

```
POST   /api/v1/auth/register           # 회원가입
POST   /api/v1/auth/login              # 로그인
POST   /api/v1/auth/refresh            # 토큰 갱신
POST   /api/v1/auth/logout             # 로그아웃
```

### 사용자

```
GET    /api/v1/users/me                # 내 정보 조회
PUT    /api/v1/users/me                # 내 정보 수정
DELETE /api/v1/users/me                # 회원 탈퇴
```

### Agent

```
POST   /api/v1/agents                  # Agent 생성
GET    /api/v1/agents                  # Agent 목록
GET    /api/v1/agents/{id}             # Agent 상세
PUT    /api/v1/agents/{id}             # Agent 수정
DELETE /api/v1/agents/{id}             # Agent 삭제
POST   /api/v1/agents/{id}/test        # Agent 테스트
POST   /api/v1/agents/{id}/process     # RAG 처리 (파싱→청킹→임베딩)
GET    /api/v1/agents/{id}/status      # RAG 처리 상태
```

### 템플릿 (GET: 사용자, POST/PUT/DELETE: 관리자)

```
GET    /api/v1/templates               # 템플릿 목록
GET    /api/v1/templates/{id}          # 템플릿 상세
POST   /api/v1/templates               # 템플릿 생성 (AdminUser)
PUT    /api/v1/templates/{id}          # 템플릿 수정 (AdminUser)
DELETE /api/v1/templates/{id}          # 템플릿 삭제 (AdminUser)
```

### 파일

```
POST   /api/v1/files                   # 파일 업로드 (multipart)
GET    /api/v1/files                   # 파일 목록
GET    /api/v1/files/{id}              # 파일 상세
DELETE /api/v1/files/{id}              # 파일 삭제
GET    /api/v1/files/{id}/download     # 파일 다운로드
```

### 채팅

```
POST   /api/v1/chat/sessions                   # 세션 생성
GET    /api/v1/chat/sessions                   # 세션 목록
GET    /api/v1/chat/sessions/{id}/messages     # 메시지 조회
POST   /api/v1/chat/sessions/{id}/messages     # 메시지 전송 (SSE)
DELETE /api/v1/chat/sessions/{id}              # 세션 삭제
```

### 대시보드

```
GET    /api/v1/dashboard/summary               # 사용량 요약
GET    /api/v1/dashboard/usage/timeseries      # 일별 추이
GET    /api/v1/dashboard/usage/by-agent        # Agent별 분포
```

### 관리자 - 모델 관리

```
POST   /api/v1/admin/models                    # 모델 등록
GET    /api/v1/admin/models                    # 모델 목록
PUT    /api/v1/admin/models/{id}               # 모델 수정
DELETE /api/v1/admin/models/{id}               # 모델 삭제
POST   /api/v1/admin/models/{id}/test          # 모델 연결 테스트
GET    /api/v1/admin/models/openrouter/available  # Open Router 모델 조회
```

### 관리자 - 대시보드 / 토큰 제한

```
GET    /api/v1/admin/dashboard/summary         # 전체 현황
GET    /api/v1/admin/dashboard/usage/timeseries # 전체 사용량 추이
GET    /api/v1/admin/dashboard/usage/by-user   # 사용자별 분포

POST   /api/v1/admin/token-limits              # 제한 설정 생성
GET    /api/v1/admin/token-limits              # 제한 설정 목록
PUT    /api/v1/admin/token-limits/{id}         # 제한 설정 수정
DELETE /api/v1/admin/token-limits/{id}         # 제한 설정 삭제
```

---

## 데이터베이스 스키마

총 13개 테이블 (PostgreSQL 15 + pgvector):

| 테이블 | 설명 | 삭제 방식 |
|--------|------|-----------|
| users | 사용자 계정 (email PK) | soft delete (use_yn) |
| models | LLM/임베딩 모델 (관리자 등록) | soft delete |
| templates | Agent 템플릿 (시스템 5종 + 관리자 추가) | soft delete |
| agents | Agent 설정 | soft delete |
| agent_tools | Agent에 연결된 Tool | soft delete |
| agent_files | Agent-File 연결 | soft delete |
| agent_sub_agents | Agent 부모-자식 관계 | soft delete |
| files | 업로드 파일 메타데이터 | hard delete |
| snap_vec_ebd | 벡터 임베딩 (agent_id 파티셔닝) | soft delete |
| chat_sessions | 채팅 세션 | soft delete |
| chat_messages | 채팅 메시지 | soft delete |
| usage_logs | 토큰 사용량 로그 | hard delete |
| token_limits | 토큰 제한 설정 (관리자) | soft delete |

### 공통 컬럼 (AuditMixin)

```
created_by    VARCHAR  -- users.email FK
created_at    TIMESTAMPTZ  -- server_default=now()
updated_by    VARCHAR  -- users.email FK
updated_at    TIMESTAMPTZ  -- onupdate=now()
use_yn        CHAR(1)  -- 'Y'(활성) / 'N'(삭제)
```

---

## 핵심 정책

- **SQLAlchemy**: Mapped 스타일 전용, Relationship 사용 금지 (명시적 JOIN), AsyncSession + asyncpg
- **Soft Delete**: 모든 쿼리에 `use_yn == 'Y'` 필터 필수
- **인증**: JWT access_token(30분) + refresh_token(7일), bcrypt 직접 사용
- **API 응답 형식**: `{ "success": true, "data": {...} }` / `{ "success": false, "error": {...} }`
- **템플릿**: 관리자만 CRUD 가능, 서버 시작 시 시스템 템플릿 자동 시드

---

## 환경변수

```env
# Database
POSTGRES_USER=snapuser
POSTGRES_PASSWORD=snappassword
POSTGRES_DB=snapagentdb

# Backend
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=<Fernet 32-byte base64 key>

# Open Router
OPENROUTER_API_KEY=your-openrouter-api-key

# CORS
CORS_ORIGINS=http://localhost:3001,http://localhost:5174

# Frontend
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

---

## 관련 프로젝트

| 프로젝트 | 설명 |
|----------|------|
| [SnapAgent](https://github.com/jaegun9593/SnapAgent.git) | 메인 프로젝트 (Frontend + Backend) |
| [SnapAgentAdmin](https://github.com/jaegun9593/SnapAgentAdmin.git) | 관리자 Frontend (별도 repo) |
