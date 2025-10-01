"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Baby, Sparkles, Heart, MessageSquare, Users } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function Home() {
  const { user, isAuthenticated, loading } = useAuth();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 relative overflow-hidden">
      {/* Decorative floating elements */}
      <div className="absolute top-10 left-10 text-6xl animate-float opacity-20">✨</div>
      <div className="absolute top-20 right-10 text-5xl animate-float opacity-20" style={{ animationDelay: '1s' }}>🌟</div>
      <div className="absolute bottom-32 left-16 text-5xl animate-float opacity-20" style={{ animationDelay: '2s' }}>💕</div>
      <div className="absolute bottom-40 right-20 text-4xl animate-float opacity-20" style={{ animationDelay: '0.5s' }}>🍼</div>

      <div className="text-center mb-8 relative z-10">
        <div className="inline-block mb-6 p-6 bg-white/40 backdrop-blur-sm rounded-full shadow-lg animate-pulse-gentle">
          <Baby className="w-20 h-20 text-pink-500" strokeWidth={1.5} />
        </div>

        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
          BabyPolicy
        </h1>

        <div className="flex items-center justify-center gap-2 mb-6">
          <Sparkles className="w-5 h-5 text-yellow-400" />
          <p className="text-lg text-gray-700 font-medium">
            우리 아이를 위한 정책, 한눈에!
          </p>
          <Sparkles className="w-5 h-5 text-yellow-400" />
        </div>

        <p className="text-base text-gray-600 max-w-md mx-auto mb-2">
          육아 정책을 쉽고 빠르게 찾아드려요
        </p>
        <div className="flex items-center justify-center gap-1 text-sm text-gray-500">
          <Heart className="w-4 h-4 text-red-400 fill-red-400" />
          <span>부모님을 위한 친절한 AI 도우미</span>
        </div>
      </div>

      {!loading && (
        <div className="w-full max-w-xs space-y-3 relative z-10">
          {!isAuthenticated ? (
            <>
              <Button
                asChild
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-pink-400 to-pink-500 hover:from-pink-500 hover:to-pink-600 shadow-lg hover:shadow-xl transition-all duration-300 rounded-2xl"
              >
                <Link href="/login">로그인</Link>
              </Button>
              <Button
                asChild
                variant="outline"
                className="w-full h-12 text-lg font-semibold border-2 border-pink-300 bg-white/70 backdrop-blur-sm hover:bg-pink-50 hover:border-pink-400 transition-all duration-300 rounded-2xl"
              >
                <Link href="/register">회원가입</Link>
              </Button>
            </>
          ) : (
            <>
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 mb-4 shadow-md border border-pink-100">
                <p className="text-sm text-gray-600 mb-1">환영합니다!</p>
                <p className="text-lg font-bold text-gray-800">
                  {user?.name || user?.email || "사용자"}님
                </p>
              </div>
              <Button
                asChild
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-purple-400 to-purple-500 hover:from-purple-500 hover:to-purple-600 shadow-lg hover:shadow-xl transition-all duration-300 rounded-2xl"
              >
                <Link href="/chat">
                  <MessageSquare className="w-5 h-5 mr-2" />
                  AI 챗봇 시작하기
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                className="w-full h-12 text-lg font-semibold border-2 border-blue-300 bg-white/70 backdrop-blur-sm hover:bg-blue-50 hover:border-blue-400 transition-all duration-300 rounded-2xl"
              >
                <Link href="/community">
                  <Users className="w-5 h-5 mr-2" />
                  커뮤니티 둘러보기
                </Link>
              </Button>
            </>
          )}

          {!isAuthenticated && (
            <div className="pt-4 text-center">
              <Link
                href="/chat"
                className="text-sm text-blue-500 hover:text-blue-600 underline underline-offset-4 font-medium"
              >
                둘러보기 →
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
