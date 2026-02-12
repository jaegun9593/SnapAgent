# SnapAgent - Agent Builder

## 프로젝트 개요

RAG Agent Builder - 사용자가 RAG, 웹검색, 도구사용 기반의 AI Agent를 직접 생성하고 운영할 수 있는 플랫폼.
모든 Agent는 ReAct(Reasoning + Acting) 패턴으로 동작하며, 의도 분류 → Tool 실행 → 답변 평가 → 재질의 순환 루프를 포함한다.
SnapRAG(`/Users/jaekeon/project/workspace/SnapRAG`) 프로젝트의 디자인/구조를 참조하여 구축.

## 리포지토리

| 프로젝트 | URL | 설명 |
|----------|-----|------|
| SnapAgent | https://github.com/jaegun9593/SnapAgent.git | 메인 프로젝트 (Frontend + Backend) |
| SnapAgentAdmin | https://github.com/jaegun9593/SnapAgentAdmin.git | 관리자 Frontend (별도 repo) |

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React 19, Vite, TypeScript, Zustand, React Query (TanStack), Tailwind CSS, shadcn/ui, Recharts |
| Admin Frontend | React 19, Vite, TypeScript, Zustand, React Query, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI, Python 3.12+, SQLAlchemy 2.0 (async), LangChain, LangGraph |
| Database | PostgreSQL 15+ with pgvector |
| Auth | JWT (python-jose + bcrypt) |
| LLM Router | Open Router API 연동 |
| Infra | Docker, Docker Compose |

## 디렉토리 구조

```
SnapAgent/
├── backend/                           # FastAPI Backend (공용)
│   ├── app/
│   │   ├── main.py                    # FastAPI 엔트리포인트
│   │   ├── config.py                  # 환경변수 설정 (Pydantic Settings)
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py          # API 라우터 통합
│   │   │       ├── auth.py            # 인증 (회원가입/로그인/토큰갱신)
│   │   │       ├── users.py           # 사용자 관리
│   │   │       ├── agents.py          # Agent CRUD, 테스트
│   │   │       ├── templates.py       # Agent 템플릿 관리
│   │   │       ├── files.py           # 파일 업로드/관리
│   │   │       ├── chat.py            # Agent 채팅 (SSE 스트리밍)
│   │   │       ├── dashboard.py       # 사용자 대시보드
│   │   │       ├── admin/             # 관리자 전용 API
│   │   │       │   ├── router.py      # Admin 라우터
│   │   │       │   ├── models.py      # 모델 관리 (Open Router)
│   │   │       │   ├── dashboard.py   # 관리자 대시보드
│   │   │       │   └── token_limits.py # 토큰 제한 설정
│   │   │       └── deps.py            # 의존성 주입 (인증, DB세션)
│   │   ├── core/
│   │   │   ├── security.py            # JWT 토큰 + bcrypt 패스워드
│   │   │   ├── encryption.py          # Fernet 암호화 (API키)
│   │   │   └── exceptions.py          # 커스텀 예외 클래스
│   │   ├── db/
│   │   │   ├── base.py                # Base 모델 + AuditMixin
│   │   │   ├── database.py            # Async DB 세션 설정
│   │   │   ├── models.py              # SQLAlchemy ORM 모델
│   │   │   └── vector_models.py       # 벡터 관련 모델
│   │   ├── schemas/                   # Pydantic DTO
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── agent.py
│   │   │   ├── template.py
│   │   │   ├── file.py
│   │   │   ├── chat.py
│   │   │   ├── dashboard.py
│   │   │   ├── model.py
│   │   │   └── token_limit.py
│   │   ├── services/                  # 비즈니스 로직
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── agent_service.py
│   │   │   ├── template_service.py
│   │   │   ├── template_seed.py       # 서버 시작 시 시스템 템플릿 5종 자동 시드
│   │   │   ├── file_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── usage_service.py
│   │   │   ├── model_service.py
│   │   │   └── token_limit_service.py
│   │   ├── agent/                     # ReAct Agent 엔진
│   │   │   ├── react_agent.py         # ReAct 루프 (의도분류→Tool실행→평가→재질의)
│   │   │   ├── intent_classifier.py   # 사용자 의도 분류
│   │   │   ├── tool_executor.py       # Tool 실행 관리
│   │   │   ├── evaluator.py           # 답변 품질 평가
│   │   │   ├── token_tracker.py       # 토큰 사용량 추적
│   │   │   └── tools/                 # Agent Tools
│   │   │       ├── base.py            # BaseTool 인터페이스
│   │   │       ├── rag_tool.py        # RAG 검색 도구
│   │   │       ├── web_search_tool.py # 웹 검색 도구
│   │   │       └── custom_api_tool.py # 사용자 정의 API 도구
│   │   └── rag/                       # RAG 파이프라인
│   │       ├── parsing.py             # 문서 파싱 (PDF, DOCX, CSV 등)
│   │       ├── chunking.py            # 텍스트 청킹
│   │       ├── embedding.py           # 임베딩 생성
│   │       ├── vectorstore.py         # pgvector 저장/조회
│   │       ├── retriever.py           # 시맨틱 검색
│   │       └── ocr.py                 # OCR (Tesseract, Google Vision)
│   ├── sql/                           # DB 초기화 SQL
│   │   ├── 00_init.sql                # 확장 모듈 (uuid-ossp, pgvector)
│   │   ├── 01_users.sql
│   │   ├── 02_files.sql
│   │   ├── 03_models.sql
│   │   ├── 04_templates.sql
│   │   ├── 05_agents.sql
│   │   ├── 06_agent_tools.sql
│   │   ├── 07_agent_files.sql
│   │   ├── 08_agent_sub_agents.sql
│   │   ├── 09_snap_vec_ebd.sql
│   │   ├── 10_chat_sessions.sql
│   │   ├── 11_chat_messages.sql
│   │   ├── 12_usage_logs.sql
│   │   └── 13_token_limits.sql
│   ├── docker/
│   │   ├── Dockerfile.dev
│   │   └── Dockerfile.prd
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/                          # SnapAgent 사용자 Frontend
│   ├── src/
│   │   ├── App.tsx                    # 라우팅
│   │   ├── main.tsx                   # 엔트리포인트
│   │   ├── types/
│   │   │   └── index.ts              # 공통 타입 정의
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── MyAgentsPage.tsx       # 내 Agent 목록
│   │   │   ├── AgentChatPage.tsx      # Agent 채팅
│   │   │   ├── AgentCreatePage.tsx    # Agent 생성 위자드
│   │   │   ├── TemplatesPage.tsx      # 템플릿 목록
│   │   │   ├── DashboardPage.tsx      # 마이페이지 > 대시보드
│   │   │   ├── MyPage.tsx             # 마이페이지
│   │   │   └── MyPageEdit.tsx         # 회원정보 수정
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui 컴포넌트
│   │   │   ├── layout/
│   │   │   │   ├── MainLayout.tsx     # 메인 레이아웃
│   │   │   │   ├── Header.tsx         # 상단 (로고 + 우측 마이페이지/로그아웃 버튼)
│   │   │   │   └── Sidebar.tsx        # 좌측 네비게이션
│   │   │   ├── auth/
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── agent/
│   │   │   │   ├── AgentCard.tsx
│   │   │   │   ├── AgentCreateWizard.tsx  # 생성 위자드 컨테이너
│   │   │   │   ├── steps/
│   │   │   │   │   ├── BasicInfoStep.tsx  # 기본정보 + 시스템프롬프트
│   │   │   │   │   ├── FileUploadStep.tsx # 파일 등록 (RAG용)
│   │   │   │   │   ├── ToolSelectStep.tsx # Tool 선택
│   │   │   │   │   ├── ModelSelectStep.tsx # 모델 선택
│   │   │   │   │   └── TestStep.tsx       # Agent 테스트
│   │   │   │   └── SubAgentSelector.tsx   # 서브에이전트 선택
│   │   │   ├── chat/
│   │   │   │   ├── ChatPanel.tsx          # 채팅 패널
│   │   │   │   ├── ChatMessage.tsx        # 메시지 버블
│   │   │   │   ├── ChatInput.tsx          # 입력창
│   │   │   │   ├── ToolExecutionLayer.tsx # Tool 실행 결과 접이식 레이어
│   │   │   │   └── ToolExecutionDetail.tsx # Tool 실행 상세 내역
│   │   │   ├── dashboard/
│   │   │   │   ├── UsageSummaryCard.tsx
│   │   │   │   ├── TokenUsageChart.tsx
│   │   │   │   ├── AgentCallChart.tsx
│   │   │   │   └── CostEstimationCard.tsx
│   │   │   └── template/
│   │   │       ├── TemplateCard.tsx
│   │   │       └── TemplateCreateDialog.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useUser.ts
│   │   │   ├── useAgents.ts
│   │   │   ├── useTemplates.ts
│   │   │   ├── useFiles.ts
│   │   │   ├── useChat.ts
│   │   │   └── useDashboard.ts
│   │   ├── services/
│   │   │   ├── authService.ts
│   │   │   ├── userService.ts
│   │   │   ├── agentService.ts
│   │   │   ├── templateService.ts
│   │   │   ├── fileService.ts
│   │   │   ├── chatService.ts
│   │   │   └── dashboardService.ts
│   │   ├── stores/
│   │   │   └── authStore.ts           # Zustand (토큰 + 사용자 상태)
│   │   └── lib/
│   │       ├── axios.ts               # Axios 인터셉터 (토큰 자동 갱신)
│   │       ├── queryClient.ts         # React Query 설정
│   │       └── utils.ts               # cn() 등 유틸
│   ├── docker/
│   │   ├── Dockerfile.dev
│   │   └── Dockerfile.prd
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── eslint.config.js
│   └── components.json               # shadcn/ui 설정
│
├── docker-compose.local.yml           # 로컬환경 (DB만 Docker)
├── docker-compose.dev.yml             # 개발환경 (db + backend + frontend)
├── docker-compose.prd.yml             # 운영환경
├── scripts/
│   ├── local-start.sh                 # 로컬 개발 시작 (DB Docker + 호스트 backend/frontend)
│   └── local-stop.sh                  # 로컬 개발 중지
├── .env.example
├── .gitignore
├── CLAUDE.md                          # 이 파일
└── README.md
```

---

## 핵심 정책 (SnapRAG 계승)

### 1. SQLAlchemy 정책
- **Relationship 사용 금지**: AuditMixin의 created_by/updated_by FK 충돌 방지. 명시적 JOIN 사용.
- **Mapped 스타일**: `Mapped[Type]` + `mapped_column()` 사용 (Column() 금지)
- **Async 전용**: AsyncSession, asyncpg 드라이버

### 2. Soft Delete
- 모든 테이블에 `use_yn` 컬럼 (`'Y'`=활성, `'N'`=삭제)
- 모든 쿼리에서 `use_yn == 'Y'` 필터 필수

### 3. AuditMixin (공통 컬럼)
```python
class AuditMixin:
    created_by: Mapped[str]            # users.email FK
    created_at: Mapped[datetime]       # TIMESTAMPTZ, server_default=now()
    updated_by: Mapped[Optional[str]]  # users.email FK
    updated_at: Mapped[Optional[datetime]]  # onupdate=now()
    use_yn: Mapped[str]                # 'Y' or 'N', default='Y'
```

### 4. 인증
- **JWT**: access_token(30분) + refresh_token(7일)
- **비밀번호**: bcrypt 직접 사용 (passlib 아님)
- **사용자 식별**: email을 PK로 사용
- **역할**: `role` 컬럼 (`user` / `admin`)

### 5. API 응답 형식
```json
// 성공
{ "success": true, "data": { ... } }

// 에러
{ "success": false, "error": { "code": "ERROR_CODE", "message": "...", "details": {} } }
```

### 6. 벡터 저장소
- `snap_vec_ebd` 테이블: agent_id 기반 LIST 파티셔닝
- IVFFlat 인덱스 (코사인 유사도)
- Agent별 동적 파티션 생성

### 7. 템플릿 정책
- **관리자 전용**: 템플릿 생성/수정/삭제는 관리자(AdminUser)만 가능, 사용자는 조회만 가능
- **시스템 템플릿 자동 시드**: 서버 기동 시 `template_seed.py`에서 5종 시스템 템플릿 자동 등록 (멱등성 보장)
  - RAG 문서 검색 Agent (`rag`)
  - 웹 검색 Agent (`web_search`)
  - 하이브리드 Agent (`hybrid`)
  - 커스텀 API Agent (`custom`)
  - 범용 대화 Agent (`general`)
- **Lifespan**: `main.py`의 `lifespan` 컨텍스트 매니저에서 시드 실행, 실패해도 서버 정상 기동
- **프론트엔드**: 사용자 화면은 읽기 전용 (생성/삭제 버튼 없음), 템플릿 선택 → Agent 생성 위자드로 이동

### 8. Header UI
- 우측 상단: 이메일 표시 + 마이페이지 버튼 + 로그아웃 버튼 (드롭다운 아닌 직접 노출)

---

## 데이터베이스 스키마

### users
| 컬럼 | 타입 | 설명 |
|------|------|------|
| email | VARCHAR PK | 사용자 이메일 |
| password_hash | VARCHAR | bcrypt 해시 |
| full_name | VARCHAR | 이름 |
| role | VARCHAR | 'user' / 'admin' |
| is_active | BOOLEAN | 활성 상태 |
| + AuditMixin |

### models (관리자 등록)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| name | VARCHAR | 모델 표시명 |
| provider | VARCHAR | 'openrouter' |
| model_id | VARCHAR | Open Router 모델 ID |
| model_type | VARCHAR | 'llm' / 'embedding' |
| config | JSONB | 기본 설정 (temperature 등) |
| pricing | JSONB | 토큰당 비용 정보 |
| is_active | BOOLEAN | 사용 가능 여부 |
| + AuditMixin |

### templates
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| name | VARCHAR | 템플릿명 |
| description | TEXT | 설명 |
| tool_config | JSONB | 기본 Tool 구성 |
| system_prompt_template | TEXT | 시스템 프롬프트 템플릿 |
| category | VARCHAR | 'rag' / 'web_search' / 'hybrid' / 'custom' / 'general' |
| is_system | BOOLEAN | 시스템 기본 제공 여부 |
| + AuditMixin |

### agents
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| name | VARCHAR | Agent 이름 |
| description | TEXT | 설명 |
| system_prompt | TEXT | 시스템 프롬프트 |
| template_id | UUID FK | 사용한 템플릿 |
| model_id | UUID FK | LLM 모델 |
| embedding_model_id | UUID FK | 임베딩 모델 (RAG용) |
| config | JSONB | temperature, max_tokens 등 |
| status | VARCHAR | 'draft' / 'active' / 'inactive' |
| + AuditMixin |

### agent_tools
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| agent_id | UUID FK | |
| tool_type | VARCHAR | 'rag' / 'web_search' / 'custom_api' |
| tool_config | JSONB | Tool별 설정 |
| is_enabled | BOOLEAN | 활성 여부 |
| sort_order | INTEGER | 순서 |
| + AuditMixin |

### agent_files
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| agent_id | UUID FK | |
| file_id | UUID FK | |
| + AuditMixin |

### agent_sub_agents
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| parent_agent_id | UUID FK | 부모 Agent |
| child_agent_id | UUID FK | 자식 Agent |
| sort_order | INTEGER | 순서 |
| + AuditMixin |

### files
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| filename | VARCHAR | 원본 파일명 |
| stored_filename | VARCHAR | 저장된 파일명 |
| file_path | VARCHAR | 저장 경로 |
| file_size | BIGINT | 바이트 |
| mime_type | VARCHAR | MIME 타입 |
| + AuditMixin |

### snap_vec_ebd (파티셔닝)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID | |
| agent_id | UUID | 파티션 키 |
| chunk_text | TEXT | 원본 텍스트 |
| embedding | VECTOR(1536) | 벡터 임베딩 |
| metadata | JSONB | 소스, 페이지 등 |
| + AuditMixin |

### chat_sessions
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| agent_id | UUID FK | |
| title | VARCHAR | 세션 제목 |
| + AuditMixin |

### chat_messages
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| session_id | UUID FK | |
| role | VARCHAR | 'user' / 'assistant' / 'system' / 'tool' |
| content | TEXT | 메시지 본문 |
| tool_calls | JSONB | Tool 실행 이력 (ReAct 추적용) |
| token_usage | JSONB | {prompt, completion, total} |
| + AuditMixin |

### usage_logs
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_email | VARCHAR FK | |
| agent_id | UUID FK | |
| model_id | VARCHAR | 사용된 모델 |
| prompt_tokens | INTEGER | |
| completion_tokens | INTEGER | |
| total_tokens | INTEGER | |
| cost | DECIMAL | 비용 |
| latency_ms | INTEGER | 응답 시간 |
| + AuditMixin |

### token_limits (관리자 설정)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_email | VARCHAR FK (nullable) | null=전체 기본값 |
| limit_type | VARCHAR | 'per_minute' / 'per_hour' / 'per_day' |
| max_tokens | INTEGER | 최대 토큰 수 |
| max_api_calls | INTEGER | 최대 API 호출 수 |
| is_active | BOOLEAN | |
| + AuditMixin |

---

## API 엔드포인트

### 인증 (Auth)
```
POST   /api/v1/auth/register          # 회원가입
POST   /api/v1/auth/login             # 로그인
POST   /api/v1/auth/refresh           # 토큰 갱신
POST   /api/v1/auth/logout            # 로그아웃
```

### 사용자 (Users)
```
GET    /api/v1/users/me               # 내 정보 조회
PUT    /api/v1/users/me               # 내 정보 수정
DELETE /api/v1/users/me               # 회원 탈퇴
```

### Agent
```
POST   /api/v1/agents                 # Agent 생성
GET    /api/v1/agents                 # Agent 목록
GET    /api/v1/agents/{id}            # Agent 상세
PUT    /api/v1/agents/{id}            # Agent 수정
DELETE /api/v1/agents/{id}            # Agent 삭제
POST   /api/v1/agents/{id}/test       # Agent 테스트 (ReAct 루프 실행)
POST   /api/v1/agents/{id}/process    # RAG 처리 시작 (파싱→청킹→임베딩)
GET    /api/v1/agents/{id}/status     # RAG 처리 상태
```

### 템플릿 (Templates) - GET: 사용자, POST/PUT/DELETE: 관리자 전용
```
POST   /api/v1/templates              # 템플릿 생성 (AdminUser)
GET    /api/v1/templates              # 템플릿 목록 (시스템 템플릿)
GET    /api/v1/templates/{id}         # 템플릿 상세
PUT    /api/v1/templates/{id}         # 템플릿 수정 (AdminUser)
DELETE /api/v1/templates/{id}         # 템플릿 삭제 (AdminUser)
```

### 파일 (Files)
```
POST   /api/v1/files                  # 파일 업로드 (multipart)
GET    /api/v1/files                  # 파일 목록
GET    /api/v1/files/{id}             # 파일 상세
DELETE /api/v1/files/{id}             # 파일 삭제
GET    /api/v1/files/{id}/download    # 파일 다운로드
```

### 채팅 (Chat)
```
POST   /api/v1/chat/sessions                      # 세션 생성
GET    /api/v1/chat/sessions                      # 세션 목록
GET    /api/v1/chat/sessions/{id}/messages        # 메시지 조회
POST   /api/v1/chat/sessions/{id}/messages        # 메시지 전송 (SSE 스트리밍)
DELETE /api/v1/chat/sessions/{id}                  # 세션 삭제
```

### 대시보드 (사용자)
```
GET    /api/v1/dashboard/summary                   # 사용량 요약
GET    /api/v1/dashboard/usage/timeseries          # 일별 추이
GET    /api/v1/dashboard/usage/by-agent            # Agent별 분포
```

### 관리자 - 모델 관리
```
POST   /api/v1/admin/models                        # 모델 등록 (Open Router)
GET    /api/v1/admin/models                        # 모델 목록
GET    /api/v1/admin/models/{id}                   # 모델 상세
PUT    /api/v1/admin/models/{id}                   # 모델 수정
DELETE /api/v1/admin/models/{id}                   # 모델 삭제
POST   /api/v1/admin/models/{id}/test              # 모델 연결 테스트
GET    /api/v1/admin/models/openrouter/available   # Open Router 사용 가능 모델 조회
```

### 관리자 - 대시보드
```
GET    /api/v1/admin/dashboard/summary             # 전체 현황 (가입자, 호출수 등)
GET    /api/v1/admin/dashboard/usage/timeseries    # 전체 사용량 추이
GET    /api/v1/admin/dashboard/usage/by-user       # 사용자별 분포
```

### 관리자 - 토큰 제한
```
POST   /api/v1/admin/token-limits                  # 제한 설정 생성
GET    /api/v1/admin/token-limits                  # 제한 설정 목록
PUT    /api/v1/admin/token-limits/{id}             # 제한 설정 수정
DELETE /api/v1/admin/token-limits/{id}             # 제한 설정 삭제
GET    /api/v1/admin/token-limits/user/{email}     # 특정 사용자 제한 조회
```

---

## ReAct Agent 엔진

### 실행 흐름
```
사용자 질문
    ↓
[1] 의도 분류 (Intent Classifier)
    - 질문 유형 판단: RAG 검색 / 웹 검색 / 일반 대화 / 복합
    ↓
[2] Tool 선택 & 실행 (Tool Executor)
    - 등록된 Tool 중 적합한 것 선택
    - RAG Tool: 벡터 검색 → 관련 문서 추출
    - Web Search Tool: 외부 검색 API 호출
    - Custom API Tool: 사용자 정의 API 호출
    ↓
[3] LLM 추론 (LangChain)
    - 시스템 프롬프트 + Tool 결과 + 사용자 질문 → LLM 호출
    - 스트리밍 응답 (SSE)
    ↓
[4] 답변 평가 (Evaluator)
    - 답변 품질 점수 산출
    - 충분하면 → 최종 답변 반환
    - 불충분하면 → [2]로 재질의 (최대 3회)
```

### Tool 실행 결과 스트리밍 (SSE 이벤트)
```
// 각 단계별 이벤트를 SSE로 스트리밍하여 프론트엔드에서 실시간 표시
event: thinking        data: {"step": "intent_classification", "content": "RAG 검색이 필요한 질문으로 분류"}
event: tool_start      data: {"tool": "rag_search", "input": {"query": "..."}}
event: tool_result     data: {"tool": "rag_search", "output": {"chunks": [...], "scores": [...]}}
event: tool_start      data: {"tool": "web_search", "input": {"query": "..."}}
event: tool_result     data: {"tool": "web_search", "output": {"results": [...]}}
event: evaluation      data: {"score": 0.85, "pass": true}
event: answer_start    data: {}
event: answer_token    data: {"token": "..."}
event: answer_end      data: {"token_usage": {"prompt": 150, "completion": 200, "total": 350}}
event: done            data: {"message_id": "..."}
```

### 프론트엔드 Tool 실행 표시 (접이식 레이어)

Agent 추론/테스트 시 Tool 사용 결과를 **Claude 스타일의 접이식 레이어**로 표시:

```
┌─────────────────────────────────────────┐
│ 💬 사용자: "2024년 매출 현황 알려줘"        │
├─────────────────────────────────────────┤
│ ▶ 의도 분류: RAG 검색 (접기/펼치기)        │  ← 접힌 상태
│ ▼ RAG 검색 실행 (펼쳐진 상태)              │  ← 펼친 상태
│   ┌─────────────────────────────────┐    │
│   │ Query: "2024년 매출 현황"         │    │
│   │ 검색 결과: 3건                    │    │
│   │ Score: 0.92, 0.87, 0.81         │    │
│   │ Sources:                         │    │
│   │   - 매출보고서_2024.pdf (p.12)   │    │
│   │   - 분기실적_Q4.xlsx (sheet1)    │    │
│   └─────────────────────────────────┘    │
│ ▶ 답변 평가: 0.91 통과 (접기/펼치기)       │
├─────────────────────────────────────────┤
│ 🤖 어시스턴트:                             │
│ 2024년 매출 현황은 다음과 같습니다...       │
└─────────────────────────────────────────┘
```

**ToolExecutionLayer 컴포넌트 구조:**
- 기본 접힌 상태: 아이콘 + Tool명 + 소요시간 + 상태 표시
- 펼치면: 입력값, 출력값, 검색된 소스, 스코어 등 상세 정보
- 실행 중: 스피너 애니메이션
- 성공/실패: 색상으로 구분 (green/red)

---

## Docker 구성

### 포트 매핑 (SnapRAG와 충돌 방지)
| 서비스 | SnapRAG | SnapAgent | SnapAgentAdmin |
|--------|---------|-----------|----------------|
| DB | 5432 | **5433** | (공유) |
| Backend | 8000 | **8001** | (공유) |
| Frontend (dev) | 5173 | **5174** | **5175** |
| Frontend (prd) | 3000 | **3001** | **3002** |

### 로컬환경 (`docker-compose.local.yml`)
```bash
# DB만 Docker, backend/frontend는 호스트에서 직접 실행
docker-compose -f docker-compose.local.yml up -d     # DB 시작
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
cd frontend && npm run dev

# 또는 원클릭 스크립트
./scripts/local-start.sh    # 전체 시작
./scripts/local-stop.sh     # 전체 중지
```

### 개발환경 (`docker-compose.dev.yml`)
```yaml
# 모든 서비스 Docker
services:
  db:        # pgvector/pgvector:pg15, port 5433:5432
  backend:   # FastAPI + uvicorn --reload, port 8001:8000
  frontend:  # Vite dev server, port 5174
```

### 운영환경 (`docker-compose.prd.yml`)
```yaml
services:
  db:        # pgvector/pgvector:pg15, port 5433:5432
  backend:   # Gunicorn + UvicornWorker, port 8001:8000
  frontend:  # Nginx, port 3001:80
```

> **관리자 패널**: SnapAgentAdmin 별도 repo에서 독립 docker-compose로 운영
> (https://github.com/jaegun9593/SnapAgentAdmin.git)

---

## 환경변수 (.env)

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
MAX_FILE_SIZE_MB=10
LOG_LEVEL=DEBUG
ENCRYPTION_KEY=<Fernet 32-byte base64 key>

# Open Router
OPENROUTER_API_KEY=your-openrouter-api-key

# CORS
CORS_ORIGINS=http://localhost:3001,http://localhost:5174

# Frontend
VITE_API_BASE_URL=http://localhost:8001/api/v1
VITE_ENVIRONMENT=development

# Ports
FRONTEND_PORT=5173
```

---

## 참조 프로젝트

- **SnapRAG** (`/Users/jaekeon/project/workspace/SnapRAG`): UI 디자인, 컴포넌트 구조, 백엔드 아키텍처, RAG 파이프라인 참조
- 주요 참조 항목:
  - Frontend: MainLayout, Header, Sidebar, shadcn/ui 설정, Axios 인터셉터, React Query 설정
  - Backend: FastAPI 구조, 예외 처리, 인증 흐름, RAG 파이프라인 (parsing, chunking, embedding, vectorstore)
  - DB: SQLAlchemy 2.0 패턴, AuditMixin, 파티셔닝 전략
  - Docker: 개발/운영 Dockerfile, docker-compose 구성
