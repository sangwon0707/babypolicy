"use client";

import { useRouter } from "next/navigation";
import { User, Settings, Heart, MessageSquare, LogOut, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";

export default function MePage() {
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-50/30 to-pink-50/30">
        <div className="text-center">
          <div className="inline-block p-4 bg-white/70 backdrop-blur-sm rounded-full shadow-lg">
            <div className="w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
          </div>
          <p className="mt-4 text-gray-500 text-sm">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-blue-50/30 to-pink-50/30 p-6">
        <div className="text-center mb-6">
          <div className="inline-block p-6 bg-white/70 backdrop-blur-sm rounded-full shadow-lg mb-4">
            <User className="w-16 h-16 text-blue-400" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">로그인이 필요해요</h2>
          <p className="text-gray-600">맞춤 정책을 받으려면 로그인해주세요</p>
        </div>
        <Button
          onClick={() => router.push("/login")}
          className="rounded-2xl bg-gradient-to-r from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600 shadow-md px-8"
        >
          로그인하기
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50/30 to-pink-50/30 pb-20">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-blue-100 p-4 shadow-sm">
        <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <span className="text-2xl">👤</span>
          마이페이지
        </h1>
        <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
          <Sparkles className="w-3 h-3" />
          내 정보를 관리해요
        </p>
      </div>

      <div className="p-4 space-y-4">
        {/* Profile Card */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-sm border border-blue-100">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-400 rounded-full flex items-center justify-center shadow-md">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">
                {user.name || "사용자"}
              </h2>
              <p className="text-sm text-gray-500">{user.email}</p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <div className="space-y-2">
          <button className="w-full bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-blue-100 hover:border-blue-300 transition-all flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-pink-500 rounded-full flex items-center justify-center">
              <Heart className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 text-left">
              <p className="font-semibold text-gray-800">관심 정책</p>
              <p className="text-xs text-gray-500">저장한 정책을 확인하세요</p>
            </div>
          </button>

          <button className="w-full bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-blue-100 hover:border-blue-300 transition-all flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-500 rounded-full flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 text-left">
              <p className="font-semibold text-gray-800">내가 쓴 글</p>
              <p className="text-xs text-gray-500">커뮤니티 활동 내역</p>
            </div>
          </button>

          <button className="w-full bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-blue-100 hover:border-blue-300 transition-all flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-500 rounded-full flex items-center justify-center">
              <Settings className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 text-left">
              <p className="font-semibold text-gray-800">설정</p>
              <p className="text-xs text-gray-500">프로필 및 알림 설정</p>
            </div>
          </button>
        </div>

        {/* Logout */}
        <Button
          onClick={handleLogout}
          variant="outline"
          className="w-full rounded-2xl border-2 border-red-200 text-red-500 hover:bg-red-50 hover:border-red-300"
        >
          <LogOut className="w-5 h-5 mr-2" />
          로그아웃
        </Button>
      </div>
    </div>
  );
}
