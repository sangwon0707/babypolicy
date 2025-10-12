"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Target, Heart, ExternalLink, Calendar } from "lucide-react";

export default function InterestPoliciesPage() {
  const router = useRouter();

  const mockPolicies = [
    {
      id: 1,
      title: "부모급여 지원",
      category: "💰 지원금",
      amount: "월 100만원 (만 0세)",
      description: "만 0세 자녀를 가정에서 양육하는 부모에게 지급되는 현금성 지원금입니다.",
      deadline: "상시 신청",
      saved_date: "2025. 10. 10.",
    },
    {
      id: 2,
      title: "첫만남 이용권",
      category: "💰 지원금",
      amount: "200만원",
      description: "출생아 1인당 200만원을 국민행복카드 바우처 포인트로 지급합니다.",
      deadline: "출생일로부터 1년 이내",
      saved_date: "2025. 10. 09.",
    },
    {
      id: 3,
      title: "육아휴직 급여",
      category: "👨‍👩‍👧 육아지원",
      amount: "통상임금의 80% (최대 250만원)",
      description: "만 8세 이하 또는 초등학교 2학년 이하의 자녀를 돌보기 위한 휴직 시 지원됩니다.",
      deadline: "휴직 개시 전 신청",
      saved_date: "2025. 10. 08.",
    },
    {
      id: 4,
      title: "어린이집 보육료 지원",
      category: "🎓 교육지원",
      amount: "전액 무료 (0-5세)",
      description: "어린이집을 이용하는 영유아에게 보육료를 지원합니다.",
      deadline: "상시 신청",
      saved_date: "2025. 10. 07.",
    },
    {
      id: 5,
      title: "임신·출산 진료비 지원",
      category: "🏥 의료지원",
      amount: "100만원 (다태아 140만원)",
      description: "임신·출산 관련 진료비로 사용할 수 있는 바우처를 지급합니다.",
      deadline: "출산 예정일로부터 60일 이내",
      saved_date: "2025. 10. 05.",
    },
    {
      id: 6,
      title: "출산 축하금 (서울시)",
      category: "💰 지원금",
      amount: "첫째 200만원, 둘째 이상 300만원",
      description: "서울시 거주 가정에 출산을 축하하며 지급하는 축하금입니다.",
      deadline: "출생일로부터 1년 이내",
      saved_date: "2025. 10. 03.",
    },
    {
      id: 7,
      title: "국가 예방접종 지원",
      category: "🏥 의료지원",
      amount: "무료",
      description: "만 12세 이하 아동의 필수 예방접종 비용을 전액 지원합니다.",
      deadline: "상시 신청",
      saved_date: "2025. 10. 01.",
    },
    {
      id: 8,
      title: "산후조리비 지원 (강남구)",
      category: "🏥 의료지원",
      amount: "50만원",
      description: "강남구 거주 산모의 산후 건강관리 비용을 지원합니다.",
      deadline: "출산일로부터 6개월 이내",
      saved_date: "2025. 09. 28.",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-br from-pink-400 to-purple-400 px-6 pt-12 pb-8">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-white mb-6 hover:opacity-80 transition-opacity"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm">돌아가기</span>
        </button>
        <div className="flex items-center gap-3 mb-2">
          <Target className="w-8 h-8 text-white" />
          <h1 className="text-2xl font-bold text-white">관심 정책</h1>
        </div>
        <p className="text-pink-100 text-sm">
          내가 관심있어하는 정책 {mockPolicies.length}개
        </p>
      </div>

      {/* Policies List */}
      <div className="px-6 -mt-4">
        <div className="space-y-3">
          {mockPolicies.map((policy) => (
            <div
              key={policy.id}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-500">
                      {policy.category}
                    </span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-400">{policy.saved_date}</span>
                  </div>
                  <h3 className="font-bold text-gray-900 text-lg mb-1">
                    {policy.title}
                  </h3>
                  <p className="text-sm font-semibold text-pink-600 mb-2">
                    {policy.amount}
                  </p>
                </div>
                <button className="flex-shrink-0 p-2 hover:bg-pink-50 rounded-lg transition-colors">
                  <Heart className="w-5 h-5 text-pink-500 fill-pink-500" />
                </button>
              </div>

              <p className="text-sm text-gray-600 mb-3 leading-relaxed">
                {policy.description}
              </p>

              <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-orange-500" />
                  <span className="text-xs text-gray-600">
                    신청 기한: {policy.deadline}
                  </span>
                </div>
                <button className="flex items-center gap-1 text-xs font-medium text-purple-600 hover:text-purple-700">
                  자세히 보기
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Padding */}
      <div className="h-8"></div>
    </div>
  );
}
