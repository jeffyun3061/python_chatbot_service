# ── python 3.10+  FINAL VECTOR‑MEMORY VERSION ───────────────────────
"""
main.py  (백엔드)
────────
<<<<<<< HEAD
● 벡터 DB + Mongo 에 저장된 과거 대화를 컨텍스트로 사용해 GPT 호출
  ‑ 최근 20개 + 벡터 유사 5개 (사용자별 thread 기준)
● @코딩번역기 1‑회 해석 로직
"""
import os
import json
import asyncio
=======
● 벡터 DB + Mongo 에 저장된 **모든 과거 대화**를 컨텍스트로 사용해 GPT 호출
  ‑ 최근 20개 + 벡터 유사 5개 → 항상 포함
● 벡터 회상 사용
● @코딩번역기 1‑회 해석 로직 그대로 유지
"""
import os, json, asyncio
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient
import chromadb
from sentence_transformers import SentenceTransformer

# ─────────────────────────── CONSTANTS ───────────────────────────
TAG_TRANSLATE = "@코딩번역기"
<<<<<<< HEAD
BOT_NAME = "SYSTEM"
SYSTEM_PROMPT = (
    "너는 'SYSTEM' AI 비서다. 짧고 명확하게 한국어로 답한다. "
    "불필요한 설명은 생략한다."
)

translate_mode_by_user: dict[str, bool] = {}
=======
SYSTEM_PROMPT = (
    "너는 사용자의 과거 메시지와 본인의 응답을 항상 반영하여 자연스럽게 대화를 이어가는 AI 비서야."
    " 반드시 컨텍스트를 활용해 이어서 답변해."
)

is_translate_mode = False
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da

# ─────────────────────────── INIT ───────────────────────────────
load_dotenv(Path(__file__).parent / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
<<<<<<< HEAD
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MAX_TOKENS_CHAT = int(os.getenv("MAX_TOKENS_CHAT", "200"))
MAX_TOKENS_CODE = int(os.getenv("MAX_TOKENS_CODE", "400"))
RECENT_CONTEXT = int(os.getenv("RECENT_CONTEXT", "6"))
SIMILAR_CONTEXT = int(os.getenv("SIMILAR_CONTEXT", "2"))
MAX_MSG_CHARS = int(os.getenv("MAX_MSG_CHARS", "400"))

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

mongo = AsyncIOMotorClient(MONGO_URI).chat
m_col = mongo.messages
chroma = chromadb.PersistentClient(path=Path(__file__).parent / "chroma")
collection = chroma.get_or_create_collection("chat_history")
encoder = SentenceTransformer("intfloat/e5-small-v2")

# ────────────────────────── FASTAPI ─────────────────────────────
app = FastAPI(title="Solo Leveling Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
=======
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MONGO_URI      = os.getenv("MONGO_URI", "mongodb://localhost:27017")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

mongo      = AsyncIOMotorClient(MONGO_URI).chat
m_col      = mongo.messages
chroma     = chromadb.PersistentClient(path=Path(__file__).parent / "chroma")
collection = chroma.get_or_create_collection("chat_history")
encoder    = SentenceTransformer("intfloat/e5-small-v2")

# ────────────────────────── FASTAPI ─────────────────────────────
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
)

# ───────────────────────── DATA MODEL ───────────────────────────
class Message(BaseModel):
    type: str
    nickname: str
    message: str
    timestamp: str
    role: str  # "user" | "assistant"
    response_id: str | None = None
<<<<<<< HEAD
    thread: str | None = None

clients: List[WebSocket] = []


def msg_to_json(msg: Message) -> str:
    if hasattr(msg, "model_dump_json"):
        return msg.model_dump_json()
    return msg.json()


def msg_to_dict(msg: Message) -> dict:
    if hasattr(msg, "model_dump"):
        return msg.model_dump()
    return msg.dict()


def require_api_key():
    if not OPENAI_API_KEY or not openai_client:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되지 않았습니다. back/.env 파일을 확인하세요."
        )


def trim(text: str, limit: int = MAX_MSG_CHARS) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


# ─────────────────────── STORAGE HELPERS ────────────────────────
async def save_and_embed(msg: Message):
    res = await m_col.insert_one(msg_to_dict(msg))
=======

clients: List[WebSocket] = []

# ─────────────────────── STORAGE HELPERS ────────────────────────
async def save_and_embed(msg: Message):
    res = await m_col.insert_one(msg.dict())
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
    collection.upsert(
        ids=[str(res.inserted_id)],
        embeddings=[encoder.encode(msg.message).tolist()],
        documents=[msg.message],
<<<<<<< HEAD
        metadatas=[{
            "nickname": msg.nickname,
            "role": msg.role,
            "thread": msg.thread or msg.nickname,
        }],
    )


async def recent_context(nick: str, k: int | None = None) -> list[dict]:
    k = k or RECENT_CONTEXT
    cur = m_col.find({"thread": nick}).sort("timestamp", -1).limit(k)
    docs = list(reversed(await cur.to_list(None)))
    return [
        {"role": d["role"], "content": trim(d["message"])}
        for d in docs
    ]


def similar_context(nick: str, query: str, k: int | None = None) -> list[dict]:
    k = k or SIMILAR_CONTEXT
    res = collection.query(
        query_embeddings=[encoder.encode(query).tolist()],
        n_results=k,
        where={"thread": nick},
    )
    if not res["documents"] or not res["documents"][0]:
        return []

    metas = res["metadatas"][0]
    docs = res["documents"][0]
    seen: set[str] = set()
    result = []
    for meta, doc in zip(metas, docs):
        snippet = trim(doc)
        if snippet in seen:
            continue
        seen.add(snippet)
        result.append({"role": meta.get("role", "user"), "content": snippet})
    return result


async def gpt_reply(user_text: str, nick: str) -> tuple[str, str | None]:
    require_api_key()
    user_text = trim(user_text, limit=800)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    recent = await recent_context(nick)
    messages += recent
    recent_texts = {m["content"] for m in recent}
    for item in similar_context(nick, user_text):
        if item["content"] not in recent_texts:
            messages.append(item)
=======
        metadatas=[{"nickname": msg.nickname, "role": msg.role}],
    )

async def recent_context(nick: str, k: int = 20) -> list[dict]:
    cur = m_col.find({}).sort("timestamp", -1).limit(k)
    docs = list(reversed(await cur.to_list(None)))
    return [
        {"role": d["role"], "content": d["message"]} for d in docs
    ]

def similar_context(nick: str, query: str, k: int = 5) -> list[dict]:
    res = collection.query(
        query_embeddings=[encoder.encode(query).tolist()],
        n_results=k,
    )
    return [{"role": "assistant", "content": d} for d in res["documents"][0]]

async def gpt_reply(user_text: str, nick: str) -> tuple[str, str]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += await recent_context(nick)
    messages += similar_context(nick, user_text)
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
    messages.append({"role": "user", "content": user_text})

    loop = asyncio.get_running_loop()
    resp = await loop.run_in_executor(
        None,
        partial(
            openai_client.chat.completions.create,
            model=OPENAI_MODEL,
            messages=messages,
<<<<<<< HEAD
            temperature=0.5,
            max_tokens=MAX_TOKENS_CHAT,
=======
            temperature=0.7,
            max_tokens=512,
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
        ),
    )
    txt = resp.choices[0].message.content.strip()
    return txt, resp.id

<<<<<<< HEAD

async def code_translate(code: str) -> tuple[str, str | None]:
    require_api_key()
    code = trim(code, limit=1500)
    prompt = (
        "코드를 간단히 설명해. 개요 → 핵심 로직 → 한 줄 요약 순으로, "
        "짧게 답해:\n```\n"
        f"{code}\n```"
    )

    loop = asyncio.get_running_loop()
    resp = await loop.run_in_executor(
        None,
        partial(
            openai_client.chat.completions.create,
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=MAX_TOKENS_CODE,
        ),
    )
    return resp.choices[0].message.content.strip(), resp.id


# ──────────────────────── REST ENDPOINT ─────────────────────────
@app.get("/health")
async def health():
    mongo_ok = False
    try:
        await mongo.command("ping")
        mongo_ok = True
    except Exception:
        pass

    return {
        "status": "ok" if mongo_ok else "degraded",
        "mongo": mongo_ok,
        "openai_configured": bool(OPENAI_API_KEY),
        "model": OPENAI_MODEL,
    }


=======
async def code_translate(code: str) -> str:
    prompt = f"""당신은 '코딩 번역기' 역할을 수행합니다. 아래 요구사항을 반드시 지켜 설명하세요.

1. **전체 개요** …
2. **라인-바이-라인 해설** (➤ 기호) …
3. **변수·함수 이름 번역** …
4. **용어 풀이** …
5. **최종 흐름** …
6. **추가 학습 포인트** …:\n```python\n{code}\n```"""
    resp = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=800,
    )
    return resp.choices[0].message.content.strip(), resp.id

# ──────────────────────── REST ENDPOINT ─────────────────────────
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
@app.get("/messages")
async def get_messages():
    docs = await m_col.find().sort("timestamp", 1).to_list(None)
    for d in docs:
        d["_id"] = str(d["_id"])
    return JSONResponse(docs)

<<<<<<< HEAD

=======
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
# ─────────────────────── WEBSOCKET LOOP ─────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
<<<<<<< HEAD
=======
    global is_translate_mode
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            data.setdefault("timestamp", datetime.utcnow().isoformat())
<<<<<<< HEAD
            data.setdefault("thread", data.get("nickname"))

            user_msg = Message(**data, role="user")
            await save_and_embed(user_msg)
            await asyncio.gather(*[c.send_text(msg_to_json(user_msg)) for c in clients])

            nick = user_msg.nickname

            try:
                if user_msg.message.strip() == TAG_TRANSLATE:
                    translate_mode_by_user[nick] = True
                    bot_text = (
                        "[QUEST] 코딩 번역기 모드 활성화.\n"
                        "다음 메시지에 코드를 입력하면 해석해 드립니다."
                    )
                    resp_id = None
                elif translate_mode_by_user.pop(nick, False):
                    bot_text, resp_id = await code_translate(user_msg.message)
                else:
                    bot_text, resp_id = await gpt_reply(user_msg.message, nick)
            except Exception as exc:
                bot_text = f"[SYSTEM ERROR] {exc}"
                resp_id = None

            bot_msg = Message(
                type="chat",
                nickname=BOT_NAME,
                message=bot_text,
                timestamp=datetime.utcnow().isoformat(),
                role="assistant",
                response_id=resp_id,
                thread=nick,
            )
            await save_and_embed(bot_msg)
            await asyncio.gather(*[c.send_text(msg_to_json(bot_msg)) for c in clients])
=======

            user_msg = Message(**data, role="user")
            await save_and_embed(user_msg)
            await asyncio.gather(*[c.send_text(user_msg.json()) for c in clients])

            # ── TAG 처리 ──────────────────────────
            if user_msg.message.strip() == TAG_TRANSLATE:
                is_translate_mode = True
                bot_text = "🧠 코딩을 완벽히 해석해 드립니다! 다음 입력한 코드를 설명할게요."
                resp_id = None
            elif is_translate_mode:
                bot_text, resp_id = await code_translate(user_msg.message)
                is_translate_mode = False
            else:
                bot_text, resp_id = await gpt_reply(user_msg.message, user_msg.nickname)

            bot_msg = Message(
                type="chat", nickname="ChatGPT", message=bot_text,
                timestamp=datetime.utcnow().isoformat(), role="assistant", response_id=resp_id
            )
            await save_and_embed(bot_msg)
            await asyncio.gather(*[c.send_text(bot_msg.json()) for c in clients])
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da

    except WebSocketDisconnect:
        clients.remove(ws)

<<<<<<< HEAD

# ────────────────────────── DEV RUN ─────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
=======
# ────────────────────────── DEV RUN ─────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("back.main:app", host="127.0.0.1", port=8000, reload=True)
>>>>>>> e3e9a29a53e42ea119cb98bc24f9c7c67932c4da
