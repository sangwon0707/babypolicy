"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Clock, AlertCircle, Calendar, ExternalLink, Bell } from "lucide-react";

export default function UpcomingDeadlinesPage() {
  const router = useRouter();

  const mockDeadlines = [
    {
      id: 1,
      title: "임신·출산 진료비 바우처 사용 기한",
      category: "🏥 의료지원",
      deadline: "2025. 11. 15.",
      daysLeft: 34,
      urgency: "normal",
      description: "출산 예정일 기준 60일 이내 사용해야 합니다.",
      status: "미신청",
    },
    {
      id: 2,
      title: "첫만남 이용권 신청 마감",
      category: "💰 지원금",
      deadline: "2025. 11. 20.",
      daysLeft: 39,
      urgency: "normal",
      description: "출생일로부터 1년 이내 신청 필수",
      status: "미신청",
    },
    {
      id: 3,
      title: "육아휴직 급여 신청",
      category: "👨‍👩‍👧 육아지원",
      deadline: "2025. 10. 25.",
      daysLeft: 13,
      urgency: "high",
      description: "휴직 개시 1개월 전 신청 권장",
      status: "준비중",
    },
    {
      id: 4,
      title: "서울시 출산 축하금 신청",
      category: "💰 지원금",
      deadline: "2025. 12. 31.",
      daysLeft: 80,
      urgency: "low",
      description: "출생일로부터 1년 이내 신청",
      status: "미신청",
    },
    {
      id: 5,
      title: "강남구 산후조리비 지원 신청",
      category: "🏥 의료지원",
      deadline: "2025. 10. 28.",
      daysLeft: 16,
      urgency: "high",
      description: "출산일로부터 6개월 이내 신청",
      status: "서류 준비중",
    },
  ];

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "high":
        return "bg-red-500";
      case "normal":
        return "bg-orange-500";
      case "low":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  const getUrgencyBg = (urgency: string) => {
    switch (urgency) {
      case "high":
        return "bg-red-50 border-red-200";
      case "normal":
        return "bg-orange-50 border-orange-200";
      case "low":
        return "bg-blue-50 border-blue-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-br from-orange-400 to-red-400 px-6 pt-12 pb-8">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-white mb-6 hover:opacity-80 transition-opacity"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm">돌아가기</span>
        </button>
        <div className="flex items-center gap-3 mb-2">
          <Clock className="w-8 h-8 text-white" />
          <h1 className="text-2xl font-bold text-white">다가오는 마감일</h1>
        </div>
        <p className="text-orange-100 text-sm">
          마감 예정 정책 {mockDeadlines.length}개
        </p>
      </div>

      {/* Alert Banner */}
      <div className="px-6 -mt-4 mb-4">
        <div className="bg-gradient-to-r from-red-500 to-orange-500 rounded-2xl p-4 shadow-lg">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-white mb-1">긴급 신청 필요</h3>
              <p className="text-sm text-white/90">
                2주 이내 마감되는 정책이 2개 있습니다. 서둘러 신청하세요!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Deadlines List */}
      <div className="px-6">
        <div className="space-y-3">
          {mockDeadlines
            .sort((a, b) => a.daysLeft - b.daysLeft)
            .map((deadline) => (
              <div
                key={deadline.id}
                className={`bg-white rounded-2xl p-5 shadow-sm border hover:shadow-md transition-shadow ${getUrgencyBg(
                  deadline.urgency
                )}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-medium text-gray-500">
                        {deadline.category}
                      </span>
                      <span
                        className={`text-xs font-semibold text-white px-2 py-0.5 rounded-full ${getUrgencyColor(
                          deadline.urgency
                        )}`}
                      >
                        D-{deadline.daysLeft}
                      </span>
                    </div>
                    <h3 className="font-bold text-gray-900 text-lg mb-1">
                      {deadline.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      {deadline.description}
                    </p>
                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white rounded-lg border border-gray-200">
                      <span className="text-xs font-medium text-gray-600">
                        {deadline.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 pt-3 border-t border-gray-200">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-orange-500" />
                    <span className="text-xs text-gray-600">
                      마감일: {deadline.deadline}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-4">
                  <button className="py-2 bg-white hover:bg-gray-50 rounded-xl flex items-center justify-center gap-1.5 text-sm font-medium text-gray-700 border border-gray-200 transition-colors">
                    <Bell className="w-4 h-4" />
                    알림 설정
                  </button>
                  <button className="py-2 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 rounded-xl flex items-center justify-center gap-1.5 text-sm font-medium text-white transition-colors">
                    <ExternalLink className="w-4 h-4" />
                    바로 신청
                  </button>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Info Card */}
      <div className="px-6 mt-6">
        <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-5 border border-amber-100">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
              <Bell className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">알림 설정 안내</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                중요한 신청 마감일을 놓치지 않도록 알림을 설정하세요. 마감 7일 전, 3일 전, 1일 전에 알림을 받을 수 있습니다.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Padding */}
      <div className="h-8"></div>
    </div>
  );
}
