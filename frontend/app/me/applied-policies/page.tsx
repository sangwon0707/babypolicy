"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, CheckCircle2, FileText, Calendar, ExternalLink } from "lucide-react";

export default function AppliedPoliciesPage() {
  const router = useRouter();

  const mockAppliedPolicies = [
    {
      id: 1,
      title: "부모급여 지원",
      category: "💰 지원금",
      amount: "월 100만원",
      status: "승인 완료",
      statusColor: "bg-green-500",
      applied_date: "2025. 09. 15.",
      approved_date: "2025. 09. 20.",
      description: "매월 25일 지급 예정",
    },
    {
      id: 2,
      title: "첫만남 이용권",
      category: "💰 지원금",
      amount: "200만원",
      status: "지급 완료",
      statusColor: "bg-blue-500",
      applied_date: "2025. 08. 10.",
      approved_date: "2025. 08. 15.",
      description: "국민행복카드로 사용 가능",
    },
    {
      id: 3,
      title: "어린이집 보육료 지원",
      category: "🎓 교육지원",
      amount: "전액 무료",
      status: "승인 완료",
      statusColor: "bg-green-500",
      applied_date: "2025. 07. 05.",
      approved_date: "2025. 07. 10.",
      description: "2025년 12월까지 지원",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-400 to-indigo-400 px-6 pt-12 pb-8">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-white mb-6 hover:opacity-80 transition-opacity"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm">돌아가기</span>
        </button>
        <div className="flex items-center gap-3 mb-2">
          <CheckCircle2 className="w-8 h-8 text-white" />
          <h1 className="text-2xl font-bold text-white">신청 완료</h1>
        </div>
        <p className="text-purple-100 text-sm">
          신청한 정책 {mockAppliedPolicies.length}개
        </p>
      </div>

      {/* Applied Policies List */}
      <div className="px-6 -mt-4">
        <div className="space-y-3">
          {mockAppliedPolicies.map((policy) => (
            <div
              key={policy.id}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-medium text-gray-500">
                      {policy.category}
                    </span>
                    <span
                      className={`text-xs font-semibold text-white px-2 py-0.5 rounded-full ${policy.statusColor}`}
                    >
                      {policy.status}
                    </span>
                  </div>
                  <h3 className="font-bold text-gray-900 text-lg mb-1">
                    {policy.title}
                  </h3>
                  <p className="text-sm font-semibold text-purple-600 mb-1">
                    {policy.amount}
                  </p>
                  <p className="text-xs text-gray-500">{policy.description}</p>
                </div>
              </div>

              <div className="space-y-2 pt-3 border-t border-gray-100">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-gray-400" />
                  <span className="text-xs text-gray-600">
                    신청일: {policy.applied_date}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-gray-600">
                    승인일: {policy.approved_date}
                  </span>
                </div>
              </div>

              <button className="w-full mt-4 py-2.5 bg-gradient-to-r from-purple-50 to-indigo-50 hover:from-purple-100 hover:to-indigo-100 rounded-xl flex items-center justify-center gap-2 text-sm font-medium text-purple-700 transition-colors">
                <ExternalLink className="w-4 h-4" />
                신청 내역 자세히 보기
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Info Card */}
      <div className="px-6 mt-6">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-5 border border-blue-100">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">신청 내역 관리</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                신청한 정책의 진행 상황을 확인하고, 필요한 서류나 추가 정보를 업데이트할 수 있습니다.
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
