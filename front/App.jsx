import React, { useCallback, useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function App() {
  const [dark, setDark] = useState(true);
  const [nick, setNick] = useState("");
  const [confirmed, setConfirmed] = useState(() => localStorage.getItem("nickname") || "");
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(null);

  const ws = useRef(null);
  const bottom = useRef(null);
  const reconnectDelay = useRef(1000);

  useEffect(() => {
    const controller = new AbortController();

    (async () => {
      try {
        const res = await fetch(`${API_BASE}/messages`, { signal: controller.signal });
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        const data = await res.json();
        setChat(data);
      } catch (e) {
        console.error(e);
        setError("서버에 연결할 수 없습니다.");
      }
    })();

    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!confirmed.trim()) return;

    let socket;
    let closedByUser = false;

    const connect = () => {
      socket = new WebSocket(`${API_BASE.replace(/^http/, "ws")}/ws`);
      ws.current = socket;

      socket.onopen = () => {
        setReady(true);
        reconnectDelay.current = 1000;
      };

      socket.onclose = () => {
        setReady(false);
        if (!closedByUser) {
          setTimeout(connect, reconnectDelay.current);
          reconnectDelay.current = Math.min(reconnectDelay.current * 2, 16000);
        }
      };

      socket.onerror = (e) => {
        console.error(e);
        socket.close();
      };

      socket.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          setChat((prev) => [...prev, msg]);
        } catch (err) {
          console.error("Invalid JSON:", err);
        }
      };
    };

    connect();

    return () => {
      closedByUser = true;
      socket && socket.close();
    };
  }, [confirmed]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const send = useCallback(() => {
    if (!confirmed.trim()) return alert("닉네임 먼저!");
    if (!input.trim()) return;

    if (!ready || !ws.current || ws.current.readyState !== WebSocket.OPEN) {
      return alert("서버 연결 중입니다. 잠시 후 다시 시도하세요.");
    }

    ws.current.send(
      JSON.stringify({
        type: "chat",
        nickname: confirmed,
        message: input,
        timestamp: new Date().toISOString(),
      })
    );
    setInput("");
  }, [confirmed, input, ready]);

  const confirmNick = useCallback(() => {
    if (!nick.trim()) return;
    localStorage.setItem("nickname", nick);
    setConfirmed(nick);
  }, [nick]);

  return (
    <div className={`container ${dark ? "dark" : "light"}`}>
      <h2>Chatting</h2>

      <button className="mode-toggle" onClick={() => setDark(!dark)}>
        {dark ? "☀️ 라이트모드" : "🌙 다크모드"}
      </button>

      <div className="nickname-bar">
        <input
          placeholder="닉네임 입력"
          value={nick}
          onChange={(e) => setNick(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && confirmNick()}
        />
        <button onClick={confirmNick}>Enter</button>
      </div>

      <div className="chat-box">
        {error && <div className="message error">{error}</div>}
        {chat.map((m, idx) => {
          const mine = m.nickname === confirmed;
          const ai = m.nickname === "ChatGPT";
          return (
            <div
              key={`${m.timestamp}-${idx}`}
              className={`message ${mine ? "mine" : "other"} ${ai ? "ai" : ""}`}
            >
              {ai && <span className="ai-orb" />}
              <strong>{m.nickname}</strong>
              <span>[{new Date(m.timestamp).toLocaleTimeString()}] : </span>
              {m.message}
            </div>
          );
        })}
        <div ref={bottom} />
      </div>

      <div className="input-bar">
        <input
          placeholder="메시지를 입력하세요"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => !e.nativeEvent.isComposing && e.key === "Enter" && send()}
          disabled={!confirmed}
        />
        <button onClick={send} disabled={!confirmed}>
          Send
        </button>
      </div>
    </div>
  );
}
