import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
const BOT_NAMES = ["SYSTEM", "ChatGPT"];

function calcStats(chat, nickname) {
  const mine = chat.filter((m) => m.nickname === nickname);
  const quests = chat.filter(
    (m) => BOT_NAMES.includes(m.nickname) && (m.thread === nickname || !m.thread)
  ).length;
  const msgCount = mine.length;
  const level = Math.floor(msgCount / 5) + 1;
  const exp = (msgCount % 5) * 20;

  return { level, exp, msgCount, quests };
}

export default function App() {
  const [dark, setDark] = useState(true);
  const [nick, setNick] = useState("");
  const [confirmed, setConfirmed] = useState(() => localStorage.getItem("nickname") || "");
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(null);
  const [apiReady, setApiReady] = useState(null);

  const ws = useRef(null);
  const bottom = useRef(null);
  const reconnectDelay = useRef(1000);

  const stats = useMemo(
    () => calcStats(chat, confirmed),
    [chat, confirmed]
  );

  useEffect(() => {
    const controller = new AbortController();

    (async () => {
      try {
        const [msgRes, healthRes] = await Promise.all([
          fetch(`${API_BASE}/messages`, { signal: controller.signal }),
          fetch(`${API_BASE}/health`, { signal: controller.signal }),
        ]);

        if (!msgRes.ok) throw new Error(`${msgRes.status} ${msgRes.statusText}`);
        const data = await msgRes.json();
        setChat(data);

        if (healthRes.ok) {
          const health = await healthRes.json();
          setApiReady(health.openai_configured);
          if (!health.openai_configured) {
            setError("OpenAI API 키가 설정되지 않았습니다. back/.env 를 확인하세요.");
          }
        }
      } catch (e) {
        console.error(e);
        setError("서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인하세요.");
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
    if (!confirmed.trim()) return alert("헌터 이름(닉네임)을 먼저 등록하세요!");
    if (!input.trim()) return;

    if (!ready || !ws.current || ws.current.readyState !== WebSocket.OPEN) {
      return alert("SYSTEM 연결 중입니다. 잠시 후 다시 시도하세요.");
    }

    ws.current.send(
      JSON.stringify({
        type: "chat",
        nickname: confirmed,
        message: input,
        timestamp: new Date().toISOString(),
        thread: confirmed,
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
    <div className={`app-shell ${dark ? "dark" : "light"}`}>
      <div className="container">
        <header className="system-header">
          <div className="system-badge">SYSTEM</div>
          <h1>PLAYER STATUS</h1>
          <p className="system-sub">AI 비서와 대화하며 퀘스트를 진행하세요</p>
        </header>

        {confirmed && (
          <div className="status-panel">
            <div className="stat">
              <span className="stat-label">HUNTER</span>
              <strong>{confirmed}</strong>
            </div>
            <div className="stat">
              <span className="stat-label">LEVEL</span>
              <strong>Lv.{stats.level}</strong>
            </div>
            <div className="stat">
              <span className="stat-label">EXP</span>
              <div className="exp-bar">
                <div className="exp-fill" style={{ width: `${stats.exp}%` }} />
              </div>
              <span className="exp-text">{stats.exp}%</span>
            </div>
            <div className="stat">
              <span className="stat-label">QUEST</span>
              <strong>{stats.quests} 완료</strong>
            </div>
          </div>
        )}

        <div className="connection-row">
          <span className={`status-dot ${ready ? "online" : "offline"}`} />
          <span>{ready ? "SYSTEM ONLINE" : "CONNECTING..."}</span>
          {apiReady === false && <span className="api-warn">API KEY 필요</span>}
          <button className="mode-toggle" onClick={() => setDark(!dark)}>
            {dark ? "☀️ LIGHT" : "🌙 DARK"}
          </button>
        </div>

        {!confirmed && (
          <div className="quest-banner">
            [QUEST] 헌터 등록 — 닉네임을 입력하고 Enter를 누르세요
          </div>
        )}

        <div className="nickname-bar">
          <input
            placeholder="헌터 이름 입력"
            value={nick}
            onChange={(e) => setNick(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && confirmNick()}
          />
          <button onClick={confirmNick}>REGISTER</button>
        </div>

        <div className="chat-box">
          {error && <div className="message error">{error}</div>}
          {confirmed && chat.length === 0 && !error && (
            <div className="message system-msg">
              <span className="quest-tag">[DAILY QUEST]</span>
              SYSTEM과 대화를 시작하세요. <code>@코딩번역기</code> 로 코드 해석도 가능합니다.
            </div>
          )}
          {chat.map((m, idx) => {
            const mine = m.nickname === confirmed;
            const ai = BOT_NAMES.includes(m.nickname);
            const displayName = ai ? "SYSTEM" : m.nickname;
            return (
              <div
                key={`${m.timestamp}-${idx}`}
                className={`message ${mine ? "mine" : "other"} ${ai ? "ai" : ""}`}
              >
                {ai && <span className="ai-orb" />}
                <strong>{displayName}</strong>
                <span className="msg-time">[{new Date(m.timestamp).toLocaleTimeString()}]</span>
                <div className="msg-body">{m.message}</div>
              </div>
            );
          })}
          <div ref={bottom} />
        </div>

        <div className="input-bar">
          <input
            placeholder={confirmed ? "SYSTEM에 메시지 입력..." : "먼저 헌터 등록이 필요합니다"}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => !e.nativeEvent.isComposing && e.key === "Enter" && send()}
            disabled={!confirmed}
          />
          <button onClick={send} disabled={!confirmed}>
            SEND
          </button>
        </div>
      </div>
    </div>
  );
}
