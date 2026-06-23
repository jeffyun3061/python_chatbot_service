# Solo Leveling System UI Chatbot

나혼자만레벨업의 **SYSTEM UI 느낌**을 참고해서 만든 실시간 AI 챗봇 프로젝트입니다.

단순히 GPT 응답만 붙인 챗봇이 아니라,
사용자별 대화 기록을 저장하고 이전 대화를 벡터 검색으로 다시 꺼내 쓰는 구조까지 붙여봤습니다.

FastAPI와 WebSocket으로 실시간 채팅을 처리하고,
MongoDB에는 대화 기록을 저장하며, ChromaDB는 과거 대화 유사도 검색용 메모리로 사용합니다.
프론트는 React 기반으로 만들었고, Parcel로 간단하게 실행할 수 있게 구성했습니다.

---

## 주요 기능

### 실시간 채팅

FastAPI WebSocket을 사용해서 브라우저와 서버가 실시간으로 메시지를 주고받습니다.
사용자가 메시지를 보내면 서버에서 GPT 응답을 생성한 뒤 다시 클라이언트로 전달합니다.

### 대화 기억

모든 대화는 MongoDB에 저장됩니다.
이후 사용자가 다시 질문하면 ChromaDB에서 이전 대화 중 비슷한 내용을 검색해서 GPT 응답에 참고 정보로 넣습니다.

즉, 단순 채팅이 아니라 “이전에 무슨 이야기를 했는지 어느 정도 기억하는 챗봇”을 목표로 만들었습니다.

### `@코딩번역기`

채팅창에 `@코딩번역기`를 입력하면 다음 메시지를 코드 해석 모드로 처리합니다.

예를 들어 Java, Python, JavaScript 코드 등을 붙여넣으면
코드가 어떤 흐름으로 동작하는지, 핵심 로직이 무엇인지 풀어서 설명하도록 만들었습니다.

### SYSTEM UI 테마

나혼자만레벨업의 시스템창 느낌을 참고해서 UI를 구성했습니다.

레벨, EXP, QUEST 같은 요소를 넣어서 일반 챗봇보다 게임 UI처럼 보이게 만들었습니다.
기능적으로 꼭 필요한 요소라기보다는 프로젝트의 콘셉트를 살리기 위한 화면 구성입니다.

---

## 사용 기술

### Backend

* Python
* FastAPI
* WebSocket
* MongoDB
* ChromaDB
* OpenAI API

### Frontend

* React
* Parcel
* CSS

### 기타

* dotenv
* 로컬 MongoDB 또는 MongoDB Atlas 사용 가능

---

## 프로젝트 구조

```text
python_chatbot_service-main/
├── back/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── chroma/
│
├── front/
│   ├── App.jsx
│   ├── App.css
│   └── index.html
│
├── start-backend.ps1
├── start-front.ps1
└── README.md
```

### back

FastAPI 서버 코드가 들어 있습니다.
WebSocket 연결, OpenAI API 호출, MongoDB 저장, ChromaDB 검색 로직을 처리합니다.

### front

React 화면 코드가 들어 있습니다.
닉네임 등록, 채팅 UI, SYSTEM 테마 화면을 담당합니다.

### chroma

ChromaDB가 사용하는 로컬 벡터 저장소입니다.
처음 실행하면 자동으로 생성됩니다.

---

## 실행 전 준비

아래 환경이 필요합니다.

* Python 3.10 이상
* Node.js 18 이상
* MongoDB
* OpenAI API Key

MongoDB는 로컬에 설치해서 써도 되고, Atlas를 사용해도 됩니다.

---

## 환경 변수 설정

백엔드 폴더로 이동한 뒤 `.env.example`을 복사해서 `.env` 파일을 만듭니다.

```powershell
cd back
copy .env.example .env
```

`.env` 파일에는 아래 값을 넣습니다.

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
MONGO_URI=mongodb://localhost:27017
```

OpenAI API 키가 없으면 화면은 뜨지만 GPT 응답은 정상적으로 나오지 않습니다.
그래서 실제 채팅 기능을 테스트하려면 API 키 설정이 필요합니다.

`.env` 파일은 GitHub에 올리면 안 되기 때문에 `.gitignore`에 포함했습니다.

---

## 백엔드 실행

```powershell
cd back
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

또는 프로젝트 루트에서 아래 스크립트를 실행해도 됩니다.

```powershell
.\start-backend.ps1
```

서버가 정상적으로 실행되면 아래 주소로 상태를 확인할 수 있습니다.

```text
GET http://localhost:8000/health
```

응답 예시는 아래와 같습니다.

```json
{
  "status": "ok",
  "mongo": true,
  "openai_configured": true,
  "model": "gpt-4o-mini"
}
```

여기서 `mongo`가 `true`면 MongoDB 연결이 된 상태이고,
`openai_configured`가 `true`면 API 키가 정상적으로 읽힌 상태입니다.

---

## 프론트엔드 실행

```powershell
cd front
npm install
npm start
```

또는 프로젝트 루트에서 아래 스크립트를 실행할 수 있습니다.

```powershell
.\start-front.ps1
```

Parcel 기본 포트는 보통 아래 주소입니다.

```text
http://localhost:1234
```

---

## 사용 방법

1. 브라우저에서 프론트 화면 접속
2. 닉네임 입력 후 REGISTER
3. 채팅창에 메시지 입력
4. SYSTEM이 GPT 응답을 반환
5. `@코딩번역기` 입력 후 코드를 붙여넣으면 코드 해석 모드로 동작

---

## 동작 흐름

전체 흐름은 아래와 같습니다.

```text
사용자 메시지 입력
        ↓
React에서 WebSocket으로 서버에 전송
        ↓
FastAPI WebSocket 엔드포인트에서 메시지 수신
        ↓
MongoDB에 대화 저장
        ↓
ChromaDB에서 관련 과거 대화 검색
        ↓
검색된 기억 + 현재 질문을 GPT 요청에 포함
        ↓
OpenAI API 응답 생성
        ↓
응답을 다시 WebSocket으로 프론트에 전달
        ↓
채팅 UI에 출력
```

이 구조로 만든 이유는 단순히 “질문 → GPT 답변”이 아니라,
이전 대화를 어느 정도 참고하는 챗봇 구조를 직접 실험해보고 싶었기 때문입니다.

---

## 만들면서 신경 쓴 부분

### 1. WebSocket 기반 실시간 응답

REST API로도 채팅은 만들 수 있지만,
채팅 서비스에 더 가까운 구조를 경험해보고 싶어서 WebSocket을 사용했습니다.

### 2. MongoDB와 ChromaDB 역할 분리

MongoDB는 원본 대화 저장용으로 사용했고,
ChromaDB는 유사도 검색을 위한 벡터 메모리 용도로 사용했습니다.

처음에는 하나의 DB에 전부 넣는 방식도 생각했지만,
원본 데이터 저장과 검색용 벡터 저장은 역할이 다르다고 판단해서 분리했습니다.

### 3. 코드 번역 모드

일반 채팅과 코드 해석 요청을 구분하기 위해 `@코딩번역기` 명령어를 만들었습니다.
명령어 입력 후 다음 메시지를 별도 모드로 처리하는 방식이라,
나중에 다른 명령어를 추가하기도 쉬운 구조입니다.

### 4. 콘셉트 있는 UI

기능만 있는 챗봇보다 기억에 남는 프로젝트로 보이게 하고 싶어서
SYSTEM UI 콘셉트를 넣었습니다.

다만 UI 콘셉트가 핵심은 아니고,
핵심은 WebSocket, GPT API 연동, DB 저장, 벡터 검색 구조를 연결해본 점입니다.

---

## 자주 발생한 문제

### OpenAI API 키 오류

`.env`에 API 키가 없거나 잘못 들어가 있으면 GPT 응답이 나오지 않습니다.

이 경우 백엔드 로그나 `/health` 결과에서 `openai_configured` 값을 확인합니다.

### MongoDB 연결 오류

MongoDB가 실행 중이 아니면 대화 저장이 되지 않습니다.

로컬 MongoDB를 사용하는 경우 MongoDB 서비스가 켜져 있는지 확인해야 합니다.
Atlas를 사용하는 경우 `MONGO_URI` 주소와 접속 권한을 확인해야 합니다.

### 프론트에서 서버 연결 실패

백엔드가 8000 포트에서 실행 중인지 확인합니다.
프론트 코드에서 WebSocket 주소가 백엔드 주소와 맞는지도 확인해야 합니다.

### 첫 실행이 느린 경우

임베딩 모델을 처음 사용할 때 다운로드가 발생할 수 있습니다.
이 경우 첫 실행만 시간이 조금 걸리고, 이후에는 더 빠르게 실행됩니다.

---

## 비용 관련

이 프로젝트는 OpenAI API를 사용하기 때문에 실제 GPT 응답을 생성할 때 비용이 발생합니다.

기본 모델은 `gpt-4o-mini`를 사용하도록 설정했습니다.
비교적 저렴한 모델이지만, API 키가 외부에 노출되면 원하지 않는 과금이 발생할 수 있으므로 주의해야 합니다.

---

## 앞으로 개선해보고 싶은 부분

* 사용자별 메모리 관리 고도화
* 대화 요약 저장 기능 추가
* WebSocket 연결 예외 처리 개선
* 채팅 응답 스트리밍 처리
* Docker Compose로 실행 환경 통합
* MongoDB Atlas 배포 환경 테스트
* UI 반응형 개선
* 명령어 모드 추가

---

## 정리

이 프로젝트는 FastAPI, WebSocket, MongoDB, ChromaDB, OpenAI API를 연결해서 만든 실시간 AI 챗봇입니다.

단순한 GPT 호출 예제가 아니라,
대화 저장과 벡터 검색 기반 기억 기능을 붙여보면서
AI 챗봇 서비스가 어떤 구조로 동작하는지 직접 확인해보는 데 초점을 두었습니다.
