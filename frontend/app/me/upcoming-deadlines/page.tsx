"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Clock, AlertCircle, Calendar } from "lucide-react";

interface Deadline {
  id: number;
  title: string;
  category: string;
  deadline: string;
  daysLeft: number;
  description: string;
}

const mockDeadlines: Deadline[] = [
  {
    id: 1,
    title: "육아휴직 급여 신청",
    category: "직장",
    deadline: "2025-10-25",
    daysLeft: 12,
    description: "육아휴직 시작 후 1개월 이내 신청 필수"
  },
  {
    id: 2,
    title: "출산 축하금 신청 마감",
    category: "출산",
    deadline: "2025-11-05",
    daysLeft: 23,
    description: "출생 신고 후 3개월 이내 신청"
  }
];

export default function UpcomingDeadlinesPage() {
  const router = useRouter();

  const getUrgencyColor = (daysLeft: number) => {
    if (daysLeft <= 7) return "border-red-200 bg-red-50";
    if (daysLeft <= 14) return "border-orange-200 bg-orange-50";
    return "border-yellow-200 bg-yellow-50";
  };

  const getDaysLeftColor = (daysLeft: number) => {
    if (daysLeft <= 7) return "text-red-600 bg-red-100";
    if (daysLeft <= 14) return "text-orange-600 bg-orange-100";
    return "text-yellow-600 bg-yellow-100";
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-400 to-red-400 px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-white">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold text-white flex-1">다가오는 마감일</h1>
        </div>
      </div>

      {/* Deadline List */}
      <div className="px-6 py-4">
        <div className="bg-orange-50 border border-orange-200 rounded-2xl p-4 mb-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-orange-900 mb-1">마감일 알림</p>
            <p className="text-xs text-orange-700">
              총 <span className="font-bold">{mockDeadlines.length}개</span>의 정책 마감일이 다가오고 있습니다.
            </p>
          </div>
        </div>

        <div className="space-y-3">
          {mockDeadlines.map((deadline) => (
            <div
              key={deadline.id}
              className={`bg-white rounded-2xl p-5 shadow-sm border-2 ${getUrgencyColor(deadline.daysLeft)}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-block px-2 py-0.5 bg-orange-100 text-orange-700 text-xs font-semibold rounded">
                      {deadline.category}
                    </span>
                    <span className={`inline-block px-2 py-1 text-xs font-bold rounded ${getDaysLeftColor(deadline.daysLeft)}`}>
                      D-{deadline.daysLeft}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">{deadline.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{deadline.description}</p>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>마감: {deadline.deadline}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 pt-3 border-t border-gray-200">
                <button className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-orange-600 text-white rounded-lg text-sm font-bold hover:bg-orange-700 transition-colors">
                  <Calendar className="w-4 h-4" />
                  지금 신청하기
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-white border-2 border-orange-600 text-orange-600 rounded-lg text-sm font-bold hover:bg-orange-50 transition-colors">
                  알림 설정
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
