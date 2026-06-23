# Solo Leveling Style Chatbot

나혼자만레벨업 **SYSTEM UI** 컨셉의 AI 챗봇입니다.  
FastAPI + WebSocket + MongoDB + ChromaDB 벡터 메모리 + React(Parcel)로 구성되어 있습니다.

## 기능

- 실시간 채팅 (WebSocket)
- 과거 대화 기억 (MongoDB + 벡터 유사도 검색)
- `@코딩번역기` — 다음 메시지의 코드를 상세 해석
- SYSTEM 테마 UI (레벨, EXP, QUEST 표시)

## API 키가 필요한가?

**네, OpenAI API 키가 반드시 필요합니다.**

GPT 응답과 코드 번역 기능은 OpenAI API를 호출합니다. 키 없이는 채팅 UI는 뜨지만 AI 답변은 `[SYSTEM ERROR]` 로 표시됩니다.

### API 키 발급 방법

1. [OpenAI Platform](https://platform.openai.com/api-keys) 에서 계정 생성
2. **API Keys** 메뉴에서 새 키 생성
3. 아래 설정 파일에 붙여넣기

> ⚠️ API 키는 절대 GitHub에 올리지 마세요. `back/.env`는 `.gitignore`에 포함되어 있습니다.

## 사전 준비

| 항목 | 버전 |
|------|------|
| Python | 3.10+ |
| Node.js | 18+ |
| MongoDB | 로컬 또는 Atlas |

## 설치 및 실행

### 1. 환경 변수 설정

```powershell
cd back
copy .env.example .env
# .env 파일을 열어 OPENAI_API_KEY=sk-... 입력
```

`.env` 예시:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
MONGO_URI=mongodb://localhost:27017
```

### 2. 백엔드

```powershell
cd back
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

또는 프로젝트 루트에서:

```powershell
.\start-backend.ps1
```

### 3. 프론트엔드

```powershell
cd front
npm install
npm start
```

또는:

```powershell
.\start-front.ps1
```

브라우저에서 `http://localhost:1234` (Parcel 기본 포트) 가 열립니다.

## 상태 확인

백엔드 헬스체크:

```
GET http://localhost:8000/health
```

응답 예시:

```json
{
  "status": "ok",
  "mongo": true,
  "openai_configured": true,
  "model": "gpt-4o-mini"
}
```

## 사용법

1. **헌터 등록** — 닉네임 입력 후 REGISTER
2. 메시지 입력 → SYSTEM(AI)이 답변
3. `@코딩번역기` 입력 → 다음 메시지에 코드 붙여넣기

## 프로젝트 구조

```
python_chatbot_service-main/
├── back/
│   ├── main.py           # FastAPI 서버
│   ├── requirements.txt
│   ├── .env.example      # API 키 템플릿
│   └── chroma/           # 벡터 DB (자동 생성)
├── front/
│   ├── App.jsx           # React UI
│   ├── App.css           # SYSTEM 테마
│   └── index.html
├── start-backend.ps1
├── start-front.ps1
└── README.md
```

## 문제 해결

| 증상 | 해결 |
|------|------|
| `OPENAI_API_KEY가 설정되지 않았습니다` | `back/.env`에 키 입력 후 서버 재시작 |
| `서버에 연결할 수 없습니다` | MongoDB 실행 + 백엔드 `8000` 포트 확인 |
| Parcel 모듈 오류 | `front/node_modules` 삭제 후 `npm install` |
| 첫 실행이 느림 | `e5-small-v2` 임베딩 모델 다운로드 (1회) |

## 비용 안내

OpenAI API는 사용량에 따라 과금됩니다. `gpt-4o-mini`는 저렴한 편이지만, 키를 타인과 공유하지 마세요.
