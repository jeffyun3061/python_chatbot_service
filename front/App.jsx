import React, { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const [darkMode, setDarkMode] = useState(true);  
  const [nickname, setNickname] = useState(""); // 입력 중 닉네임
  const [confirmedNickname, setConfirmedNickname] = useState(localStorage.getItem("nickname") || "");
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const ws = useRef(null);
  const endRef = useRef(null);

  // 채팅 기록 불러오기
  useEffect(() => {
    fetch("http://localhost:8000/messages")
      .then(res => res.json())
      .then(setChatLog);
  }, []);

  // WebSocket 연결
  useEffect(() => {
    if (!confirmedNickname.trim()) return;

    const socket = new WebSocket("ws://localhost:8000/ws");
    ws.current = socket;

    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setChatLog((prev) => [...prev, data]);
    };

    return () => socket.close();
  }, [confirmedNickname]);

  // 자동 스크롤
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog]);

  const handleSend = () => {
    if (!confirmedNickname.trim()) return alert("닉네임을 먼저 입력하고 Enter를 누르세요.");
    if (!message.trim()) return;

    const payload = {
      type: "text",
      nickname: confirmedNickname,
      message,
      timestamp: new Date().toISOString(),
    };

    ws.current?.send(JSON.stringify(payload));
    setMessage("");
  };

  const handleNicknameEnter = (e) => {
    if (e.key === "Enter" && nickname.trim()) {
      localStorage.setItem("nickname", nickname);
      setConfirmedNickname(nickname);
    }
  };

  return (
    <div className={`container ${darkMode ? "dark" : "light"}`}>
      <h2>Chatting</h2>

      <button onClick={() => setDarkMode(!darkMode)} className="mode-toggle">
        {darkMode ? "☀️ 라이트모드" : "🌙 다크모드"}
      </button>

      <div className="nickname-bar">
        <input
          placeholder="닉네임 입력 후 Enter 또는 버튼 클릭"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          onKeyDown={handleNicknameEnter}
        />
        <button
          onClick={() => {
            if (!nickname.trim()) return;
            localStorage.setItem("nickname", nickname);
            setConfirmedNickname(nickname);
          }}
        >
          Enter
        </button>
      </div>

      <div className="chat-box">
        {chatLog.map((m, i) => (
          <div
            key={i}
            className={`message ${m.nickname === confirmedNickname ? "mine" : "other"}`}
          >
            <strong>{m.nickname}</strong>
            <span>[{new Date(m.timestamp).toLocaleTimeString()}] : </span>
            {m.message}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <div className="input-bar">
        <input
          placeholder="메시지를 입력하세요"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (!e.nativeEvent.isComposing && e.key === "Enter") {
              handleSend();
            }
          }}
          disabled={!confirmedNickname}
        />
        <button onClick={handleSend} disabled={!confirmedNickname}>Send</button>
      </div>
    </div>
  );
}

export default App;
