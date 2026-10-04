# 🤖 Meeting Room Agent for Maxis Contest

회의실 예약 상태를 자동으로 감지하고, AI 챗봇을 통해 자연어로 조회할 수 있는 스마트 에이전트 시스템입니다.

> **프로젝트 목표:** 복잡한 회의실 예약 현황을 실시간으로 모니터링하고, Dify Chatflow를 통해 누구나 쉽게 조회할 수 있는 환경 구축

## 🌟 주요 기능

### 1️⃣ 회의실 상태 자동 감지 (Agent Core)
- 웹 기반 회의실 예약 시스템에서 **Playwright**로 실시간 스크래핑
- 601~606호 회의실의 30분 단위 예약 상태 추적
- 변경사항 자동 감지 및 이전 상태와 비교
- 변경 발생 시 이메일 알림 발송

### 2️⃣ FastAPI 기반 REST API
```
GET  /status          → 모든 회의실의 현재 예약 상태 조회
GET  /changes         → 이전 상태 대비 변경된 회의실 정보만 반환
POST /trigger-check   → 강제로 상태 확인 및 저장 트리거
```

### 3️⃣ Dify Chatflow 연동
- **자연어 기반 조회:** "601호 지금 비어있어?" 같은 질문에 AI가 답변
- **스마트 필터링:** LLM이 사용자 질문에서 회의실 번호/시간대 추출
- **실시간 응답:** API와 LLM이 함께 동작하는 완전 자동화 챗봇

## 🏗️ 시스템 아키텍처

```
┌─────────────────────┐
│   Web UI HTML       │  (A동_회의실_예약현황_2023-10-03.html)
│ (예약현황 웹사이트)  │
└──────────┬──────────┘
           │ Playwright 스크래핑
           ↓
┌─────────────────────┐
│   Agent Core        │  (agent_core.py)
│ ┌─────────────────┐ │
│ │ scrape_status   │ │ → rooms_status.json
│ │ compare_status  │ │ → changes 감지
│ │ send_email      │ │ → 알림 발송
│ └─────────────────┘ │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  FastAPI Server     │  (meeting_room_agent_api.py)
│  localhost:8000     │
│ ┌─────────────────┐ │
│ │ GET /status     │ │
│ │ GET /changes    │ │
│ │ POST /trigger   │ │
│ └─────────────────┘ │
└──────────┬──────────┘
           │ ngrok 터널
           ↓
┌─────────────────────────────────┐
│   Dify Chatflow (Cloud)         │
│ ┌─────────────────────────────┐ │
│ │ Start → HTTP Request → LLM  │ │
│ │        → Answer             │ │
│ └─────────────────────────────┘ │
│                                 │
│ "601호 지금 비어있어?"           │
│   ↓                             │
│ "네, 601호는 지금 예약가능합니다" │
└─────────────────────────────────┘
```

## 📋 파일 구조

```
.
├── agent_core.py                           # 핵심 로직 (스크래핑, 비교, 이메일)
├── meeting_room_agent_api.py               # FastAPI 서버 (3개 엔드포인트)
├── mcp_meeting_room_skill.json             # MCP Skill 정의 (Dify용)
├── A동_회의실_예약현황_2023-10-03.html      # 소스 HTML (회의실 데이터)
├── rooms_status_prev.json                  # 이전 상태 저장 (비교용)
├── requirements.txt                        # Python 의존성
├── mise.toml                               # 환경 설정 (Python 3.12)
└── README.md                               # 이 파일
```

## 🚀 빠른 시작

### 0️⃣ 사전 요구사항
- **Python 3.12+**
- **pip** (Python 패키지 관리)
- **Dify Cloud 계정** (dify.ai)
- **ngrok** (선택사항: 로컬 서버 외부 노출용)

### 1️⃣ 설치

```bash
# 프로젝트 클론
git clone https://github.com/bigcherry24/MeetingRoomAgentForMaxisContest.git
cd MeetingRoomAgentForMaxisContest

# 가상환경 생성 및 활성화
python3.12 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (최초 1회만)
playwright install chromium
```

### 2️⃣ API 서버 실행

```bash
uvicorn meeting_room_agent_api:app --host 0.0.0.0 --port 8000 --reload
```

**확인:**
```bash
curl http://localhost:8000/status
```

예상 응답:
```json
{
  "601": ["예약가능", "예약중", ...],
  "602": [...],
  ...
}
```

### 3️⃣ 외부 접근 URL 생성 (ngrok)

```bash
# ngrok 설치 (미설치 시)
brew install ngrok  # macOS
# 또는 https://ngrok.com/download 에서 다운로드

# 터널 시작
ngrok http 8000
```

출력된 URL을 복사: `https://xxxx-yyyy-zzzz.ngrok-free.app`

### 4️⃣ Dify Chatflow 구성

자세한 가이드는 [Dify Chatflow 설정 가이드](./dify_chatflow_setup_guide.html) 를 참조하세요.

**요약:**
1. dify.ai 로그인 → Create new → Chatflow
2. HTTP Request 노드 추가: GET `https://xxxx.ngrok-free.app/status`
3. LLM 노드 추가: System Prompt에 회의실 데이터 삽입
4. Answer 노드 연결
5. Preview → 테스트 → Publish

## 📚 API 엔드포인트

### GET /status
현재 모든 회의실의 예약 상태를 조회합니다.

**요청:**
```bash
curl http://localhost:8000/status
```

**응답:**
```json
{
  "601": ["예약가능", "예약중", "예약가능", ..., "예약가능"],
  "602": ["예약가능", ...],
  "603": [...],
  "604": [...],
  "605": [...],
  "606": [...]
}
```

**슬롯 인덱스 → 시간 매핑:**
- Index 0 = 08:00
- Index 1 = 08:30
- Index 2 = 09:00
- ...
- Index 24 = 20:00
- (총 25개 슬롯, 30분 단위)

### GET /changes
이전 상태 대비 변경된 회의실 정보만 반환합니다.

**요청:**
```bash
curl http://localhost:8000/changes
```

**응답:**
```json
{
  "601": {
    "changed_slots": [
      {"index": 5, "old": "예약가능", "new": "예약중"},
      {"index": 8, "old": "예약중", "new": "예약가능"}
    ]
  },
  "602": {...}
}
```

### POST /trigger-check
강제로 상태를 확인하고 변경사항을 감지하여 저장합니다.

**요청:**
```bash
curl -X POST http://localhost:8000/trigger-check
```

**응답:**
```json
{
  "has_changed": true,
  "changes": {
    "601": {...},
    "602": {...}
  },
  "mail_sent": true
}
```

## 🔧 코어 모듈

### agent_core.py

#### 함수
- **`scrape_room_status()`** → 웹사이트에서 회의실 상태 스크래핑
- **`load_prev_status()`** → 이전 저장된 상태 로드
- **`save_status(curr_status)`** → 현재 상태 저장
- **`compare_status(prev, curr)`** → 변경사항 감지 및 반환
- **`send_email(changes)`** → 변경사항을 이메일로 발송

#### 설정 상수
```python
HTML_PATH = "A동_회의실_예약현황_2023-10-03.html"
PREV_STATUS_PATH = "rooms_status_prev.json"
EMAIL_FROM = "aurakim24@gmail.com"
EMAIL_TO = "aurakim24@gmail.com"
```

> **⚠️ 보안 주의:** `EMAIL_APP_PASSWORD`는 환경변수로 분리해야 합니다 (현재 평문 하드코딩).

### meeting_room_agent_api.py

FastAPI 기반 REST API 서버입니다.

```python
@app.get("/status")
@app.get("/changes")
@app.post("/trigger-check")
```

## 📊 Dify Chatflow 예제

### 시스템 프롬프트
```
당신은 회의실 예약 상태를 안내하는 챗봇입니다.
아래는 601~606호 회의실의 30분 단위 예약 상태입니다.
배열 인덱스는 08:00부터 30분 간격입니다 (0=08:00, 1=08:30, ... 24=20:00).
값은 "예약가능" 또는 "예약중"입니다.

회의실 데이터:
{{#fetch_room_status.body#}}

사용자가 특정 회의실 번호나 시간대를 언급하면 해당 정보만 골라 
간결하게 한국어로 답하세요.
회의실 번호가 없으면 몇 호를 찾는지 먼저 물어보세요.
목록에 없는 회의실 번호면 없는 회의실이라고 답하세요.
```

### 테스트 질문 & 예상 답변
| 질문 | 예상 답변 |
|------|---------|
| "601호 지금 비어있어?" | 601호의 현재 시간대 상태 표시 |
| "602호 오후 2시에 예약 가능해?" | 602호의 14:00~14:30 상태 확인 |
| "900호 상태 알려줘" | "900호는 목록에 없습니다" |
| "회의실 상태 알려줘" | "어느 회의실을 찾으세요?" |

## 🔌 MCP Skill 정의

`mcp_meeting_room_skill.json`에 정의된 3개 스킬:

```json
{
  "namespace": "meeting_room",
  "skills": [
    {
      "name": "get_room_status",
      "description": "현재 모든 회의실의 예약 상태를 조회합니다.",
      "route": "/status",
      "http_method": "GET"
    },
    {
      "name": "get_room_status_changes",
      "description": "이전 상태와 비교해 변경된 회의실 예약 정보를 조회합니다.",
      "route": "/changes",
      "http_method": "GET"
    },
    {
      "name": "force_trigger_room_check",
      "description": "직접 상태 비교 및 변경 발생 시 최신 저장까지 트리거합니다.",
      "route": "/trigger-check",
      "http_method": "POST"
    }
  ]
}
```

## 💡 기술 스택

| 계층 | 기술 |
|------|------|
| **API Server** | FastAPI 0.109.0, Uvicorn 0.24.0 |
| **Web Scraping** | Playwright 1.63.0 (Chromium) |
| **Data Validation** | Pydantic 2.7.0 |
| **Notification** | Yagmail 0.16.0 (이메일) |
| **AI/LLM** | Dify Cloud (ChatGPT, Claude 등) |
| **Python Version** | 3.12+ |

## 🔄 동작 흐름

### 1단계: 상태 감지
```
Playwright (HTML 스크래핑)
  ↓
rooms.json 파싱 (601~606호, 25개 슬롯)
  ↓
rooms_status_prev.json과 비교
```

### 2단계: 변경 감지
```
이전 상태와 현재 상태 비교
  ↓
슬롯별 변경사항 추출
  ↓
changes 딕셔너리 생성
```

### 3단계: 알림 & 저장
```
변경사항이 있으면:
  ├→ 이메일 발송 (yagmail)
  ├→ 현재 상태를 새로운 "이전 상태"로 저장
  └→ API 응답에 포함

변경사항이 없으면:
  └→ API는 빈 changes 반환
```

### 4단계: Chatflow 응답
```
사용자 질문 (자연어)
  ↓
API → HTTP Request → JSON 응답
  ↓
LLM이 JSON 파싱 & 사용자 질문에 맞는 답변 생성
  ↓
챗봇 답변 (한국어)
```

## 🛠️ 문제 해결

### ❌ "Connection refused"
**원인:** 로컬 API 서버 미실행  
**해결:** `uvicorn meeting_room_agent_api:app --port 8000` 실행

### ❌ "Timeout"
**원인:** Playwright 스크래핑이 느림  
**해결:** Dify HTTP Request 노드의 타임아웃을 60초로 증가

### ❌ "HTML 파일을 찾을 수 없음"
**원인:** `A동_회의실_예약현황_2023-10-03.html` 파일이 프로젝트 디렉토리에 없음  
**해결:** 파일을 프로젝트 루트 디렉토리에 복사

### ❌ "이메일 발송 실패"
**원인:** Gmail 앱 비밀번호 오류 또는 네트워크 문제  
**해결:** 
- Gmail 2단계 인증 활성화
- 앱 비밀번호 생성: https://myaccount.google.com/apppasswords
- `agent_core.py`의 `EMAIL_APP_PASSWORD` 수정

## 📈 향후 개선 사항

- [ ] 특정 회의실만 조회하는 `/status/{room_id}` 엔드포인트 추가
- [ ] 데이터베이스 연동 (SQLite/PostgreSQL) — JSON 파일 대체
- [ ] 웹 대시보드 (예약 현황 시각화)
- [ ] Slack 통합 (이메일 대신 Slack 메시지)
- [ ] 정기 스케줄링 (APScheduler) — 수동 트리거 없이 자동 감지
- [ ] Docker 컨테이너화 — 클라우드 배포
- [ ] 사용자 인증 & 권한 관리

## 📞 연락처 & 라이선스

- **개발자:** Aura Kim (aurakim24@gmail.com)
- **프로젝트:** Maxis Contest 대회 참가작
- **라이선스:** MIT

---

**🌟 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**
