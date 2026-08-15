"use client";

import React, { useState, useEffect, useRef } from "react";
import { streamAICoach, checkBackendHealth } from "@/lib/api_client";
import { Terminal, Send, Sparkles, Bot, User, ToggleLeft, ToggleRight, Loader2 } from "lucide-react";

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
    <div className="w-full h-full min-h-[420px] bg-gradient-to-b from-surface-100/90 to-surface-300/90 rounded-xl border border-hud-border/40 overflow-hidden shadow-2xl backdrop-blur-md flex flex-col">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-surface-200/90 border-b border-hud-border/30">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-quantum-cyan" />
          <span className="font-mono text-xs font-bold tracking-wider text-quantum-cyan uppercase">
            A.C.E. Socratic Copilot
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* ELI5 Toggle */}
          <button
            onClick={() => setEli5Mode(!eli5Mode)}
            className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded bg-surface-50 border border-hud-subtle/30 text-hud-text hover:text-quantum-gold transition-all"
            title="Toggle ELI5 mode (Explain Like I'm 5)"
          >
            {eli5Mode ? (
              <ToggleRight className="w-4 h-4 text-quantum-gold" />
            ) : (
              <ToggleLeft className="w-4 h-4 text-hud-muted" />
            )}
            <span>ELI5: {eli5Mode ? "ON" : "OFF"}</span>
          </button>

          {/* Core Status */}
          <div className="flex items-center gap-1.5 text-[10px] font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                isBackendOnline ? "bg-quantum-green animate-ping" : "bg-quantum-cyan"
              }`}
            />
            <span className="text-hud-muted">
              {isBackendOnline ? "ONLINE" : "LOCAL COGNITION"}
            </span>
          </div>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div
        ref={scrollRef}
        className="flex-1 p-4 overflow-y-auto space-y-3 font-mono text-xs max-h-[380px]"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-2.5 items-start ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.sender === "ai" && (
              <div className="w-6 h-6 rounded-full bg-quantum-cyan/20 border border-quantum-cyan/40 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5 text-quantum-cyan" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-lg p-3 leading-relaxed ${
                msg.sender === "user"
                  ? "bg-quantum-cyan/15 text-hud-text border border-quantum-cyan/30 rounded-tr-none"
                  : "bg-surface-200/90 text-hud-text border border-hud-subtle/40 rounded-tl-none shadow-md"
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
              <div className="text-[9px] text-hud-muted mt-1 text-right">
                {msg.timestamp}
              </div>
            </div>

            {msg.sender === "user" && (
              <div className="w-6 h-6 rounded-full bg-surface-50 border border-hud-subtle/50 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5 text-hud-text" />
              </div>
            )}
          </div>
        ))}

        {isStreaming && (
          <div className="flex items-center gap-2 text-quantum-cyan text-[11px] font-mono py-1">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>A.C.E. computing quantum insight...</span>
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="px-4 py-2 bg-surface-200/40 border-t border-hud-border/20 flex gap-1.5 overflow-x-auto">
        {quickPrompts.map((q) => (
          <button
            key={q}
            onClick={() => {
              setInputVal(q);
            }}
            className="px-2 py-1 rounded bg-surface-300 hover:bg-surface-50 text-[10px] font-mono text-hud-muted hover:text-quantum-cyan border border-hud-subtle/30 whitespace-nowrap transition-all"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={handleSend}
        className="p-3 bg-surface-200/90 border-t border-hud-border/30 flex items-center gap-2"
      >
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder="Ask A.C.E. about quantum physical intuition..."
          className="flex-1 bg-surface-300 border border-hud-subtle/50 focus:border-quantum-cyan/60 rounded-lg px-3 py-2 text-xs font-mono text-hud-text outline-none transition-all placeholder:text-hud-muted/60"
        />
        <button
          type="submit"
          disabled={!inputVal.trim() || isStreaming}
          className="p-2 rounded-lg bg-quantum-cyan text-background hover:bg-quantum-cyan/90 disabled:opacity-40 transition-all shadow-md shadow-quantum-cyan/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
