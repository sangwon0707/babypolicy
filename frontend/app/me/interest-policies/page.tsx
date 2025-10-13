"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Heart, ExternalLink, Calendar } from "lucide-react";

interface Policy {
  id: number;
  title: string;
  category: string;
  amount: string;
  deadline: string;
  description: string;
}

const mockPolicies: Policy[] = [
  {
    id: 1,
    title: "첫만남 이용권",
    category: "출산",
    amount: "200만원",
    deadline: "출생 후 1년 이내",
    description: "첫째아 출산 시 200만원 바우처 지급"
  },
  {
    id: 2,
    title: "부모급여",
    category: "양육",
    amount: "월 100만원",
    deadline: "만 2세 미만",
    description: "0~23개월 영아 월 100만원 지급"
  },
  {
    id: 3,
    title: "임신·출산 진료비 지원",
    category: "임신",
    amount: "100만원",
    deadline: "임신 확인 후",
    description: "임신·출산 관련 진료비 국민행복카드로 지원"
  },
  {
    id: 4,
    title: "육아휴직 급여",
    category: "직장",
    amount: "월 최대 150만원",
    deadline: "자녀 만 8세까지",
    description: "육아휴직 기간 동안 월 급여의 80% 지급"
  },
  {
    id: 5,
    title: "아이돌봄 서비스",
    category: "돌봄",
    amount: "시간당 1~3만원",
    deadline: "만 12세 이하",
    description: "가정방문 아이돌봄 서비스 지원"
  },
  {
    id: 6,
    title: "출산 축하금",
    category: "출산",
    amount: "첫째 50만원",
    deadline: "출생 신고 후 3개월",
    description: "지자체별 출산 축하금 지급"
  },
  {
    id: 7,
    title: "국민취업지원제도",
    category: "취업",
    amount: "월 50만원",
    deadline: "6개월간",
    description: "출산 후 재취업 지원금"
  },
  {
    id: 8,
    title: "저소득 산모 신생아 건강관리",
    category: "건강",
    amount: "최대 150만원",
    deadline: "출산 후 60일 이내",
    description: "출산 가정에 건강관리사 파견"
  },
  {
    id: 9,
    title: "영아수당",
    category: "양육",
    amount: "월 50만원",
    deadline: "만 0~1세",
    description: "0~11개월 영아 양육 지원"
  },
  {
    id: 10,
    title: "다자녀 전기요금 할인",
    category: "생활",
    amount: "월 최대 16,000원",
    deadline: "자녀 3명 이상",
    description: "다자녀 가구 전기요금 할인"
  },
  {
    id: 11,
    title: "청년내일채움공제",
    category: "청년",
    amount: "최대 3,000만원",
    deadline: "2년 근속",
    description: "청년 근로자 장기근속 지원"
  },
  {
    id: 12,
    title: "아동수당",
    category: "양육",
    amount: "월 10만원",
    deadline: "만 8세 미만",
    description: "0~95개월 아동 양육비 지원"
  }
];

export default function InterestPoliciesPage() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string>("전체");

  const categories = ["전체", "출산", "양육", "임신", "직장", "돌봄", "건강", "생활", "취업", "청년"];

  const filteredPolicies = selectedCategory === "전체"
    ? mockPolicies
    : mockPolicies.filter(p => p.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-pink-400 to-purple-400 px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center gap-3 mb-3">
          <button onClick={() => router.back()} className="text-white">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold text-white flex-1">관심 정책</h1>
        </div>

        {/* Category Filter */}
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                selectedCategory === category
                  ? "bg-white text-purple-600"
                  : "bg-white/20 text-white hover:bg-white/30"
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Policy List */}
      <div className="px-6 py-4">
        <p className="text-sm text-gray-600 mb-4">
          총 <span className="font-bold text-purple-600">{filteredPolicies.length}개</span>의 정책
        </p>

        <div className="space-y-3">
          {filteredPolicies.map((policy) => (
            <div
              key={policy.id}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:border-purple-200 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-block px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-semibold rounded">
                      {policy.category}
                    </span>
                    <span className="text-xs text-gray-500">{policy.deadline}</span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">{policy.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{policy.description}</p>
                  <p className="text-lg font-bold text-pink-600">{policy.amount}</p>
                </div>
                <button className="flex-shrink-0 ml-3 p-2 text-pink-500 hover:bg-pink-50 rounded-lg">
                  <Heart className="w-5 h-5 fill-current" />
                </button>
              </div>

              <div className="flex gap-2 pt-3 border-t border-gray-100">
                <button className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-purple-50 text-purple-600 rounded-lg text-sm font-medium hover:bg-purple-100 transition-colors">
                  <ExternalLink className="w-4 h-4" />
                  상세보기
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-pink-50 text-pink-600 rounded-lg text-sm font-medium hover:bg-pink-100 transition-colors">
                  <Calendar className="w-4 h-4" />
                  일정 추가
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}
