"use client";

import { useRouter } from "next/navigation";
import { User, Settings, Heart, MessageSquare, LogOut, Target, CheckCircle2, Clock, MessageCircle, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { useEffect, useState } from "react";

interface DashboardStats {
  recommended_policies: number;
  applied_policies: number;
  upcoming_deadlines: number;
  ai_consultations: number;
}

export default function MePage() {
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  // Real stats from API
  const [stats, setStats] = useState<DashboardStats>({
    recommended_policies: 0,
    applied_policies: 0,
    upcoming_deadlines: 0,
    ai_consultations: 0,
  });
  const [statsLoading, setStatsLoading] = useState(true);

  // Mock data for features not yet in backend
  const mockDeadlines = [
    { id: 1, title: "출산지원금 신청", dDay: 7, category: "출산" },
    { id: 2, title: "육아휴직 급여 신청", dDay: 14, category: "휴직" },
    { id: 3, title: "양육수당 재신청", dDay: 21, category: "수당" },
  ];

  const mockChecklist = [
    { id: 1, title: "산후조리원 예약", completed: true, progress: 100 },
    { id: 2, title: "출산준비물 구매", completed: true, progress: 100 },
    { id: 3, title: "출산휴가 신청", completed: false, progress: 70 },
    { id: 4, title: "건강보험 출산급여", completed: false, progress: 30 },
  ];

  // Fetch dashboard stats
  useEffect(() => {
    const fetchStats = async () => {
      if (!isAuthenticated) return;

      try {
        const token = localStorage.getItem("token");
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/user/dashboard/stats`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
      } finally {
        setStatsLoading(false);
      }
    };

    fetchStats();
  }, [isAuthenticated]);

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
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-blue-50/30 to-pink-50/30 p-6 pb-20">
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
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header with Greeting */}
      <div className="bg-gradient-to-br from-pink-400 to-purple-400 px-6 pt-12 pb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-pink-100 text-sm mb-1">나의 임신·육아 여정</p>
            <h1 className="text-2xl font-bold text-white">
              {user?.name || user?.email?.split('@')[0] || "사용자"}님
            </h1>
          </div>
          <div className="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center text-3xl">
            👶
          </div>
        </div>
        <div className="bg-white/20 backdrop-blur-sm rounded-2xl px-4 py-3 mt-4">
          <p className="text-white text-sm font-medium">
            {statsLoading ? (
              "로딩 중..."
            ) : (
              <>
                받을 수 있는 혜택 <span className="font-bold">{stats.recommended_policies}개</span> • <span className="font-bold">{stats.applied_policies}개</span> 신청 완료
              </>
            )}
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="px-6 -mt-4 mb-6">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-pink-500" />
              <p className="text-xs text-gray-500">관심 정책</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {statsLoading ? "-" : stats.recommended_policies}
            </p>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-5 h-5 text-purple-500" />
              <p className="text-xs text-gray-500">신청 완료</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {statsLoading ? "-" : stats.applied_policies}
            </p>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-orange-500" />
              <p className="text-xs text-gray-500">다가오는 마감일</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {statsLoading ? "-" : stats.upcoming_deadlines}
            </p>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <MessageCircle className="w-5 h-5 text-blue-500" />
              <p className="text-xs text-gray-500">AI 상담</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {statsLoading ? "-" : stats.ai_consultations}
            </p>
          </div>
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="px-6 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Bell className="w-5 h-5 text-orange-500" />
          <h2 className="text-lg font-bold text-gray-900">놓치면 안 되는 마감일</h2>
        </div>
        <div className="space-y-2">
          {mockDeadlines.map((deadline) => (
            <div
              key={deadline.id}
              className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center gap-3"
            >
              <div className="flex-shrink-0">
                <div className="bg-gradient-to-br from-orange-400 to-red-400 text-white rounded-xl px-3 py-2 text-center min-w-[60px]">
                  <p className="text-xs font-medium">D-{deadline.dDay}</p>
                </div>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">{deadline.title}</p>
                <p className="text-xs text-gray-500 mt-0.5">{deadline.category}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Policy Checklist */}
      <div className="px-6 mb-6">
        <h2 className="text-lg font-bold text-gray-900 mb-3">나의 정책 체크리스트</h2>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div className="space-y-4">
            {mockChecklist.map((item) => (
              <div key={item.id}>
                <div className="flex items-center gap-3 mb-2">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                      item.completed
                        ? "bg-gradient-to-br from-pink-400 to-purple-400"
                        : "border-2 border-gray-300"
                    }`}
                  >
                    {item.completed && <CheckCircle2 className="w-4 h-4 text-white" />}
                  </div>
                  <p className={`font-medium flex-1 ${item.completed ? "text-gray-400 line-through" : "text-gray-900"}`}>
                    {item.title}
                  </p>
                  <span className="text-sm font-bold text-purple-600">{item.progress}%</span>
                </div>
                <div className="ml-9">
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-pink-400 to-purple-400 rounded-full transition-all"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-6 -mt-6">
        <div className="grid grid-cols-2 gap-3 mb-6">
          <button
            onClick={() => router.push("/me/saved-policies")}
            className="bg-white rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow border border-gray-100"
          >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-100 to-pink-200 flex items-center justify-center mb-3">
              <Heart className="w-6 h-6 text-pink-600" />
            </div>
            <h3 className="font-bold text-gray-900 mb-1">관심 정책</h3>
            <p className="text-xs text-gray-500">북마크한 정책</p>
          </button>

          <button className="bg-white rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow border border-gray-100">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-100 to-purple-200 flex items-center justify-center mb-3">
              <MessageSquare className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-bold text-gray-900 mb-1">내가 쓴 글</h3>
            <p className="text-xs text-gray-500">커뮤니티 활동</p>
          </button>
        </div>
      </div>

      {/* Settings Section */}
      <div className="px-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">설정</h2>

        <div className="space-y-3">
          <button
            onClick={() => router.push("/me/edit-profile")}
            className="w-full bg-white rounded-xl p-4 border border-gray-100 hover:border-purple-200 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-100 to-cyan-100 flex items-center justify-center">
                <Settings className="w-5 h-5 text-cyan-600" />
              </div>
              <div className="flex-1 text-left">
                <h3 className="font-semibold text-gray-900">프로필 설정</h3>
                <p className="text-xs text-gray-500 mt-0.5">개인정보 및 알림 관리</p>
              </div>
            </div>
          </button>

          <button
            onClick={handleLogout}
            className="w-full bg-white rounded-xl p-4 border border-gray-100 hover:border-red-200 hover:bg-red-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
                <LogOut className="w-5 h-5 text-red-500" />
              </div>
              <div className="flex-1 text-left">
                <h3 className="font-semibold text-red-600">로그아웃</h3>
                <p className="text-xs text-gray-500 mt-0.5">계정에서 나가기</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Bottom Padding */}
      <div className="h-8"></div>
    </div>
  );
}
