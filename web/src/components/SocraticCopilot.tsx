"use client";

import React, { useState, useEffect, useRef } from "react";
import { streamAICoach, checkBackendHealth } from "@/lib/api_client";
import { Send, ToggleLeft, ToggleRight } from "lucide-react";

interface Message {
  id: string;
  sender: "ai" | "user" | "system";
  text: string;
  timestamp: string;
}

interface SocraticCopilotProps {
  latestGate: string | null;
  activeQubit: number;
  circuitSummary: string;
}

export const SocraticCopilot: React.FC<SocraticCopilotProps> = ({
  latestGate,
  activeQubit,
  circuitSummary,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m0",
      sender: "ai",
      text: "Greetings, Explorer! I am A.C.E. (Advanced Conceptual Explainer), your quantum laboratory copilot. Build a circuit or ask me about the physical principles governing superposition, entanglement, and phase interference.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [inputVal, setInputVal] = useState("");
  const [eli5Mode, setEli5Mode] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth().then(setIsBackendOnline);
  }, []);

  // Auto-scroll on messages update
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  // Trigger Socratic explanation on new gate addition
  useEffect(() => {
    if (!latestGate) return;

    const explainNewGate = async () => {
      setIsStreaming(true);
      const newMsgId = `m-${Date.now()}`;

      setMessages((prev) => [
        ...prev,
        {
          id: newMsgId,
          sender: "ai",
          text: "",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);

      await streamAICoach(
        {
          latest_gate: latestGate,
          qubit: activeQubit,
          full_circuit_desc: circuitSummary,
          eli5_mode: eli5Mode,
        },
        (chunk) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === newMsgId ? { ...msg, text: msg.text + chunk } : msg
            )
          );
        }
      );

      setIsStreaming(false);
    };

    explainNewGate();
  }, [latestGate, activeQubit, circuitSummary, eli5Mode]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = inputVal.trim();
    if (!query || isStreaming) return;

    const userMsg: Message = {
      id: `u-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal("");
    setIsStreaming(true);

    const aiMsgId = `ai-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: aiMsgId,
        sender: "ai",
        text: "",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);

    await streamAICoach(
      {
        latest_gate: query,
        qubit: activeQubit,
        full_circuit_desc: circuitSummary,
        eli5_mode: eli5Mode,
      },
      (chunk) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiMsgId ? { ...msg, text: msg.text + chunk } : msg
          )
        );
      }
    );

    setIsStreaming(false);
  };

  const quickPrompts = [
    "Explain current circuit",
    "Why is my qubit mixed?",
    "How does Hadamard create superposition?",
    "Explain quantum entanglement",
  ];

  return (
    <div className="paper-card w-full h-full min-h-[420px] flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-paper-warm border-b border-pencil">
        <h2 className="section-title text-sm m-0">Socratic Dialogue</h2>

        <div className="flex items-center gap-4">
          {/* ELI5 Toggle */}
          <button
            onClick={() => setEli5Mode(!eli5Mode)}
            className={`ink-btn flex items-center gap-1.5 px-2 py-1 text-[11px] transition-colors ${
              eli5Mode ? "text-ink-amber" : "text-ink-light"
            }`}
            title="Toggle ELI5 mode (Explain Like I'm 5)"
          >
            {eli5Mode ? (
              <ToggleRight className="w-4 h-4" />
            ) : (
               <ToggleLeft className="w-4 h-4" />
            )}
            <span>ELI5: {eli5Mode ? "ON" : "OFF"}</span>
          </button>

          {/* Core Status */}
          <div className="flex items-center gap-1.5 text-[11px] font-sans text-ink">
            <span
              className={`w-2 h-2 rounded-full ${
                isBackendOnline ? "bg-ink-teal" : "bg-pencil"
              }`}
            />
            <span>
              {isBackendOnline ? "Online" : "Local"}
            </span>
          </div>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div
        ref={scrollRef}
        className="flex-1 p-4 overflow-y-auto space-y-4 max-h-[380px] bg-paper"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 items-start ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.sender === "ai" && (
              <div className="w-7 h-7 rounded-full bg-paper border border-ink-blue flex items-center justify-center shrink-0 mt-0.5">
                <span className="font-serif font-bold text-ink-blue text-sm">S</span>
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-lg p-3 leading-relaxed ${
                msg.sender === "user"
                  ? "bg-paper-warm border border-pencil rounded-tr-none"
                  : "bg-paper-deep border-l-2 border-l-ink-blue rounded-tl-none"
              }`}
            >
              <div className="whitespace-pre-wrap font-sans text-ink text-sm">{msg.text}</div>
              <div className={`text-[9px] font-mono text-ink-faint mt-1.5 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
                {msg.timestamp}
              </div>
            </div>

            {msg.sender === "user" && (
              <div className="w-7 h-7 rounded-full bg-paper-warm border border-pencil flex items-center justify-center shrink-0 mt-0.5">
                <span className="font-serif font-bold text-ink text-sm">U</span>
              </div>
            )}
          </div>
        ))}

        {isStreaming && (
          <div className="flex items-center gap-2 text-ink-light text-xs font-mono py-1 ml-10">
            <span className="animate-pencil-write">✎ composing...</span>
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="px-4 py-2 bg-paper border-t border-pencil flex gap-2 overflow-x-auto pencil-divider">
        {quickPrompts.map((q) => (
          <button
            key={q}
            onClick={() => {
              setInputVal(q);
            }}
            className="ink-btn text-[11px] whitespace-nowrap px-3 py-1.5"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={handleSend}
        className="p-3 bg-paper-warm border-t border-pencil flex items-center gap-2"
      >
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder="Ask about quantum physical intuition..."
          className="flex-1 bg-paper border border-pencil focus:border-ink-blue focus:outline-none rounded-md px-3 py-2 text-sm font-mono text-ink transition-colors placeholder:text-ink-faint"
        />
        <button
          type="submit"
          disabled={!inputVal.trim() || isStreaming}
          className="ink-btn flex items-center justify-center p-2 rounded-md bg-ink-blue text-white hover:bg-ink-blue/90 disabled:opacity-50 transition-colors border-none"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
