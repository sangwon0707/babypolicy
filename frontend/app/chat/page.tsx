"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, Sparkles, Bot, User as UserIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { chatApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ doc_id: string; content: string; score: number }>;
}

export default function ChatPage() {
  const { token, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "안녕하세요! 👶 육아 정책에 대해 궁금한 점을 물어보세요. 지역, 소득, 가족 구성 등에 맞는 정책을 찾아드릴게요!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [loading, isAuthenticated, router]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      if (!token) {
        throw new Error("로그인이 필요합니다.");
      }

      const response = await chatApi.sendMessage(input.trim(), conversationId, token);

      const assistantMessage: Message = {
        id: Date.now().toString() + "-ai",
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }
    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now().toString() + "-error",
        role: "assistant",
        content: `죄송합니다. 오류가 발생했습니다: ${error.message || "알 수 없는 오류"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-pink-50/30 to-blue-50/30">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-pink-100 p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-pink-400 to-purple-400 rounded-xl shadow-md">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-800">육아 정책 도우미</h1>
            <p className="text-xs text-gray-500 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              AI가 맞춤 정책을 찾아드려요
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.role === "user"
                  ? "bg-gradient-to-br from-blue-400 to-blue-500"
                  : "bg-gradient-to-br from-pink-400 to-purple-400"
              }`}
            >
              {message.role === "user" ? (
                <UserIcon className="w-5 h-5 text-white" />
              ) : (
                <Bot className="w-5 h-5 text-white" />
              )}
            </div>

            <div
              className={`max-w-[75%] rounded-2xl p-4 shadow-sm ${
                message.role === "user"
                  ? "bg-gradient-to-br from-blue-400 to-blue-500 text-white"
                  : "bg-white/90 backdrop-blur-sm text-gray-800 border border-pink-100"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-pink-100 space-y-2">
                  <p className="text-xs font-semibold text-pink-600 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    참고 정책
                  </p>
                  {message.sources.slice(0, 2).map((source, idx) => (
                    <div key={idx} className="text-xs bg-pink-50 p-2 rounded-lg">
                      <p className="font-medium text-gray-700">{source.doc_id}</p>
                      <p className="text-gray-600 line-clamp-2 mt-1">{source.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-pink-400 to-purple-400">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-pink-100">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white/80 backdrop-blur-sm border-t border-pink-100 p-4 shadow-lg">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="궁금한 정책을 물어보세요..."
            className="flex-1 rounded-2xl border-pink-200 focus:border-pink-400 focus:ring-pink-400 bg-white"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="rounded-2xl bg-gradient-to-r from-pink-400 to-pink-500 hover:from-pink-500 hover:to-pink-600 shadow-md"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
        <p className="text-xs text-gray-500 text-center mt-2">
          💡 예: "서울에 사는 2자녀 가정이 받을 수 있는 지원금은?"
        </p>
      </div>
    </div>
  );
}
