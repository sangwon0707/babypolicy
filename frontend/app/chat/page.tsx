"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, Sparkles, Bot, User as UserIcon, Menu, Plus, MessageSquare, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { chatApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ doc_id: string; content: string; score: number }>;
  function_call?: {
    name: string;
    arguments: any;
  };
}

interface Conversation {
  id: string;
  title: string;
  last_message_at: string;
  created_at: string;
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
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [hoveredConvId, setHoveredConvId] = useState<string | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null);
  const [executingFunction, setExecutingFunction] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [loading, isAuthenticated, router]);

  // Load conversations when authenticated
  useEffect(() => {
    if (isAuthenticated && token) {
      loadConversations();
    }
  }, [isAuthenticated, token]);

  const loadConversations = async () => {
    try {
      if (!token) return;
      const convos = await chatApi.getConversations(token);
      setConversations(convos);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    }
  };

  const loadConversation = async (convId: string) => {
    try {
      if (!token) return;
      const msgs = await chatApi.getConversationMessages(convId, token);

      // Convert backend messages to frontend format
      const formattedMessages: Message[] = msgs.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        sources: msg.rag_sources || undefined,
        function_call: msg.function_call || undefined,
      }));

      setMessages(formattedMessages);
      setConversationId(convId);
      setIsSidebarOpen(false);
    } catch (error) {
      console.error("Failed to load conversation:", error);
    }
  };

  const startNewConversation = () => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "안녕하세요! 👶 육아 정책에 대해 궁금한 점을 물어보세요. 지역, 소득, 가족 구성 등에 맞는 정책을 찾아드릴게요!",
      },
    ]);
    setConversationId(null);
    setIsSidebarOpen(false);
  };

  const handleDeleteClick = (convId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent loading the conversation when clicking delete
    setConversationToDelete(convId);
    setDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!conversationToDelete || !token) return;

    try {
      await chatApi.deleteConversation(conversationToDelete, token);

      // If deleted conversation is currently open, start new conversation
      if (conversationId === conversationToDelete) {
        startNewConversation();
      }

      // Reload conversations list
      loadConversations();

      // Close modal
      setDeleteModalOpen(false);
      setConversationToDelete(null);
    } catch (error) {
      console.error("Failed to delete conversation:", error);
    }
  };

  const cancelDelete = () => {
    setDeleteModalOpen(false);
    setConversationToDelete(null);
  };

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
        function_call: response.function_call,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Reload conversations list to update with new conversation or message
      loadConversations();
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

  const handleExecuteFunction = async (messageId: string, functionName: string, args: any) => {
    setExecutingFunction(messageId);
    try {
      if (!token) {
        throw new Error("로그인이 필요합니다.");
      }

      const result = await chatApi.executeFunction(functionName, args, conversationId, token);

      // Add a success message
      const successMessage: Message = {
        id: Date.now().toString() + "-success",
        role: "assistant",
        content: result.message || "작업이 완료되었습니다.",
      };

      setMessages((prev) => [...prev, successMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now().toString() + "-error",
        role: "assistant",
        content: `오류가 발생했습니다: ${error.message || "알 수 없는 오류"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setExecutingFunction(null);
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
    <div className="flex flex-col h-screen bg-white relative max-w-md mx-auto">
      {/* Sidebar Overlay - Limited to mobile frame */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 max-w-md mx-auto"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Limited to mobile frame */}
      <div
        className={`fixed top-0 left-0 h-full w-80 bg-white shadow-lg z-40 transform transition-transform duration-300 max-w-md ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">대화 목록</h2>
            <button
              onClick={startNewConversation}
              className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-pink-400 to-purple-400 text-white rounded-lg hover:from-pink-500 hover:to-purple-500 transition-all"
            >
              <Plus className="w-4 h-4" />
              새 대화
            </button>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto">
            {conversations.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>대화 내역이 없습니다</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`relative group w-full text-left border-b border-gray-100 transition-colors ${
                    conversationId === conv.id ? "bg-pink-50" : "hover:bg-pink-50"
                  }`}
                  onMouseEnter={() => setHoveredConvId(conv.id)}
                  onMouseLeave={() => setHoveredConvId(null)}
                >
                  <button
                    onClick={() => loadConversation(conv.id)}
                    className="w-full p-4 pr-12"
                  >
                    <div className="font-medium text-gray-800 line-clamp-1 mb-1">
                      {conv.title || "새 대화"}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(conv.last_message_at || conv.created_at).toLocaleDateString("ko-KR", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </button>

                  {/* Delete button - shown on hover */}
                  {hoveredConvId === conv.id && (
                    <button
                      onClick={(e) => handleDeleteClick(conv.id, e)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 p-2 hover:bg-red-100 rounded-lg transition-colors group"
                      aria-label="대화 삭제"
                    >
                      <Trash2 className="w-4 h-4 text-gray-400 group-hover:text-red-500" />
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50 max-w-md mx-auto">
          {/* Modal Overlay */}
          <div
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={cancelDelete}
          />

          {/* Modal Content */}
          <div className="relative bg-white rounded-2xl p-6 m-4 shadow-xl max-w-sm w-full">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                대화 삭제
              </h3>
              <p className="text-sm text-gray-500 mb-6">
                이 대화를 삭제하시겠습니까?<br />
                삭제된 대화는 복구할 수 없습니다.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={cancelDelete}
                  className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  취소
                </button>
                <button
                  onClick={confirmDelete}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
                >
                  삭제
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header - Fixed */}
      <div className="fixed top-0 left-0 right-0 max-w-md mx-auto bg-gradient-to-r from-pink-50 to-purple-50 border-b border-pink-100 px-6 py-4 z-20">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 hover:bg-pink-100 rounded-lg transition-colors"
            aria-label="메뉴 열기"
          >
            <Menu className="w-5 h-5 text-pink-600" />
          </button>
          <h1 className="text-lg font-semibold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
            AI 챗봇
          </h1>
        </div>
      </div>

      {/* Messages - Scrollable area with padding for fixed header/input */}
      <div className="flex-1 overflow-y-auto bg-gradient-to-b from-pink-50/20 to-white pt-20 pb-28">
        <div className="min-h-full flex flex-col justify-end p-4 space-y-4">
          {/* Example Questions - Only shown when no messages yet */}
          {messages.length === 1 && messages[0].id === "welcome" && (
            <div className="space-y-6 pb-8">
              {/* Welcome Banner */}
              <div className="bg-gradient-to-r from-pink-100 to-purple-100 rounded-2xl p-6 border border-pink-200">
                <h2 className="text-xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  👶 육아정책 AI 챗봇
                </h2>
                <p className="text-sm text-gray-600 mb-4">
                  임신, 출산, 육아와 관련된 정부 지원 정책을 쉽게 찾아드려요!
                </p>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="px-3 py-1 bg-white/80 rounded-full text-pink-700">💰 지원금</span>
                  <span className="px-3 py-1 bg-white/80 rounded-full text-purple-700">🏥 의료지원</span>
                  <span className="px-3 py-1 bg-white/80 rounded-full text-pink-700">🎓 교육지원</span>
                  <span className="px-3 py-1 bg-white/80 rounded-full text-purple-700">🏠 주거지원</span>
                </div>
              </div>

              {/* Example Questions */}
              <div className="space-y-3">
                <p className="text-sm font-semibold text-gray-700 px-1">💬 이런 질문을 해보세요</p>
                <div className="grid grid-cols-1 gap-3">
                  {[
                    { emoji: "👶", question: "서울에 사는 만 2세 아이를 키우는데 받을 수 있는 정책은?" },
                    { emoji: "🤰", question: "임신 중인데 받을 수 있는 지원금이 뭐가 있나요?" },
                    { emoji: "👨‍👩‍👧", question: "첫째 출산 시 받을 수 있는 혜택 알려주세요" },
                    { emoji: "🏫", question: "어린이집 보육료 지원 대상과 금액이 궁금해요" },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setInput(item.question);
                        // Auto-send the question
                        setTimeout(() => {
                          const sendButton = document.querySelector('button[aria-label="메시지 전송"]') as HTMLButtonElement;
                          sendButton?.click();
                        }, 100);
                      }}
                      className="text-left p-4 bg-white hover:bg-pink-50 border border-gray-200 hover:border-pink-300 rounded-xl transition-all hover:shadow-md group"
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-2xl flex-shrink-0">{item.emoji}</span>
                        <span className="text-sm text-gray-700 group-hover:text-pink-700 transition-colors">
                          {item.question}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.role === "user"
                  ? "bg-gradient-to-br from-pink-400 to-purple-400"
                  : "bg-gradient-to-br from-pink-100 to-purple-100"
              }`}
              aria-hidden="true"
            >
              {message.role === "user" ? (
                <UserIcon className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-purple-600" />
              )}
            </div>

            <div
              className={`max-w-[75%] rounded-2xl p-4 ${
                message.role === "user"
                  ? "bg-gradient-to-br from-pink-400 to-purple-400 text-white"
                  : "bg-white text-gray-800 border border-pink-100"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-pink-200 space-y-2">
                  <p className="text-xs font-semibold text-purple-600">
                    📋 참고 정책
                  </p>
                  {message.sources.slice(0, 2).map((source, idx) => (
                    <div key={idx} className="text-xs bg-pink-50 p-2 rounded-lg border border-pink-100">
                      <p className="font-medium text-gray-700">{source.doc_id}</p>
                      <p className="text-gray-600 line-clamp-2 mt-1">{source.content}</p>
                    </div>
                  ))}
                </div>
              )}

              {message.function_call && message.role === "assistant" && (
                <div className="mt-3 pt-3 border-t border-pink-200">
                  <p className="text-xs font-semibold text-purple-600 mb-2">
                    📅 캘린더 일정 제안
                  </p>
                  <div className="bg-gradient-to-r from-pink-50 to-purple-50 p-3 rounded-lg border border-purple-200">
                    <p className="text-xs font-medium text-gray-700 mb-1">
                      {message.function_call.arguments.title}
                    </p>
                    {message.function_call.arguments.date && (
                      <p className="text-xs text-gray-600 mb-2">
                        📆 {new Date(message.function_call.arguments.date).toLocaleString("ko-KR", {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    )}
                    {message.function_call.arguments.description && (
                      <p className="text-xs text-gray-600 mb-2">
                        {message.function_call.arguments.description}
                      </p>
                    )}
                    <button
                      onClick={() => handleExecuteFunction(
                        message.id,
                        message.function_call!.name,
                        message.function_call!.arguments
                      )}
                      disabled={executingFunction === message.id}
                      className="w-full mt-2 px-3 py-2 bg-gradient-to-r from-pink-400 to-purple-400 hover:from-pink-500 hover:to-purple-500 text-white text-xs font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {executingFunction === message.id ? (
                        <span className="flex items-center justify-center gap-2">
                          <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          추가 중...
                        </span>
                      ) : (
                        "✅ 캘린더에 추가"
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3" role="status" aria-live="polite" aria-label="AI가 답변을 작성하고 있습니다">
            <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-pink-100 to-purple-100" aria-hidden="true">
              <Bot className="w-4 h-4 text-purple-600" />
            </div>
            <div className="bg-white rounded-2xl p-4 border border-pink-100">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
              </div>
            </div>
          </div>
        )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input - Fixed at bottom above BottomNav */}
      <div className="fixed bottom-16 left-0 right-0 max-w-md mx-auto bg-white border-t border-pink-100 p-4 pb-safe z-20">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="메시지를 입력하세요"
            aria-label="메시지 입력"
            className="flex-1 h-12 rounded-lg border-pink-100 focus:border-pink-400 focus:ring-pink-400 bg-pink-50/50"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            aria-label="메시지 전송"
            className="min-w-[48px] min-h-[48px] rounded-lg bg-gradient-to-r from-pink-400 to-purple-400 hover:from-pink-500 hover:to-purple-500 active:from-pink-400 active:to-purple-400 disabled:opacity-50 disabled:cursor-not-allowed p-0 flex items-center justify-center transition-all shadow-sm"
          >
            <Send className="w-5 h-5 text-white" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
