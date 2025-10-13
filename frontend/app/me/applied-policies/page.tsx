"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, CheckCircle2, Calendar, FileText } from "lucide-react";

interface AppliedPolicy {
  id: number;
  title: string;
  category: string;
  appliedDate: string;
  status: "승인" | "검토중" | "추가서류필요";
  amount: string;
}

const mockAppliedPolicies: AppliedPolicy[] = [
  {
    id: 1,
    title: "부모급여",
    category: "양육",
    appliedDate: "2025-09-15",
    status: "승인",
    amount: "월 100만원"
  },
  {
    id: 2,
    title: "임신·출산 진료비 지원",
    category: "임신",
    appliedDate: "2025-08-20",
    status: "승인",
    amount: "100만원"
  },
  {
    id: 3,
    title: "육아휴직 급여",
    category: "직장",
    appliedDate: "2025-10-01",
    status: "검토중",
    amount: "월 최대 150만원"
  }
];

export default function AppliedPoliciesPage() {
  const router = useRouter();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "승인": return "bg-green-100 text-green-700";
      case "검토중": return "bg-yellow-100 text-yellow-700";
      case "추가서류필요": return "bg-orange-100 text-orange-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-400 to-pink-400 px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-white">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold text-white flex-1">신청 완료</h1>
        </div>
      </div>

      {/* Policy List */}
      <div className="px-6 py-4">
        <p className="text-sm text-gray-600 mb-4">
          총 <span className="font-bold text-purple-600">{mockAppliedPolicies.length}개</span>의 정책 신청
        </p>

        <div className="space-y-3">
          {mockAppliedPolicies.map((policy) => (
            <div
              key={policy.id}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-block px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-semibold rounded">
                      {policy.category}
                    </span>
                    <span className={`inline-block px-2 py-0.5 text-xs font-semibold rounded ${getStatusColor(policy.status)}`}>
                      {policy.status}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">{policy.title}</h3>
                  <p className="text-sm text-gray-500 mb-2">신청일: {policy.appliedDate}</p>
                  <p className="text-lg font-bold text-purple-600">{policy.amount}</p>
                </div>
                <div className="flex-shrink-0 ml-3">
                  <CheckCircle2 className={`w-8 h-8 ${policy.status === "승인" ? "text-green-500" : "text-gray-300"}`} />
                </div>
              </div>

              <div className="flex gap-2 pt-3 border-t border-gray-100">
                <button className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-purple-50 text-purple-600 rounded-lg text-sm font-medium hover:bg-purple-100 transition-colors">
                  <FileText className="w-4 h-4" />
                  신청서 보기
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-pink-50 text-pink-600 rounded-lg text-sm font-medium hover:bg-pink-100 transition-colors">
                  <Calendar className="w-4 h-4" />
                  일정 관리
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
