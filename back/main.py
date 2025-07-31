from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel

app = FastAPI()

# CORS 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메모리 상 채팅 기록 저장
chat_log = []

class Message(BaseModel):
    type: str
    nickname: str
    message: str
    timestamp: str

# 연결된 클라이언트 WebSocket 목록
connected_clients: List[WebSocket] = []

@app.get("/messages")
async def get_messages():
    return JSONResponse(content=chat_log)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            chat_data = Message.parse_raw(data)
            chat_log.append(chat_data.dict())

            # 모든 클라이언트에게 메시지 브로드캐스트
            for client in connected_clients:
                await client.send_text(data)

    except WebSocketDisconnect:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
