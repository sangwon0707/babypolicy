"use client";

import Link from "next/link";
import { MessageSquare, Users, Sparkles, Baby } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function Home() {
  const { user, isAuthenticated, loading } = useAuth();

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {!loading && (
        <>
          {!isAuthenticated ? (
            <div className="fixed inset-0 flex items-center justify-center bg-white pb-16">
              {/* Main Content - Centered */}
              <div className="flex flex-col items-center px-6 max-w-md w-full">
                {/* App Icon */}
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-pink-400 to-purple-400 mb-6 shadow-md">
                  <Baby className="w-8 h-8 text-white" />
                </div>

                {/* Title */}
                <h1 className="text-4xl font-bold text-gray-900 mb-3 tracking-tight">
                  BabyPolicy
                </h1>

                {/* Subtitle */}
                <p className="text-base text-gray-500 mb-10 text-center">
                  AI가 찾아주는 맞춤 육아 정책
                </p>

                {/* Features - Compact */}
                <div className="space-y-4 w-full mb-10">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-pink-50 flex items-center justify-center flex-shrink-0">
                      <Sparkles className="w-4 h-4 text-pink-600" />
                    </div>
                    <p className="text-sm text-gray-700">AI 맞춤 정책 추천</p>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                      <Users className="w-4 h-4 text-blue-600" />
                    </div>
                    <p className="text-sm text-gray-700">육아 커뮤니티</p>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-50 flex items-center justify-center flex-shrink-0">
                      <span className="text-lg">💰</span>
                    </div>
                    <p className="text-sm text-gray-700">최신 정책 업데이트</p>
                  </div>
                </div>

                {/* CTA Buttons */}
                <div className="space-y-3 w-full">
                  <button
                    className="w-full h-13 bg-gradient-to-r from-pink-400 to-purple-400 text-white text-base font-semibold rounded-xl hover:shadow-lg active:scale-[0.98] transition-all"
                    onClick={() => window.location.href = '/login'}
                  >
                    시작하기
                  </button>
                  <div className="text-center pt-1">
                    <Link
                      href="/chat"
                      className="text-sm text-gray-400 hover:text-gray-600 font-medium"
                    >
                      둘러보기
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="pb-20 bg-gray-50">
              {/* Hero Section */}
              <div className="bg-gradient-to-br from-pink-400 to-purple-400 px-6 pt-12 pb-8">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-pink-100 text-sm mb-1">안녕하세요</p>
                    <h1 className="text-2xl font-bold text-white">
                      {user?.name || user?.email?.split('@')[0] || "사용자"}님
                    </h1>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                    <Baby className="w-6 h-6 text-white" />
                  </div>
                </div>
              </div>

              {/* This Week's New Policies Section */}
              <div className="px-6 mt-6 mb-8">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">💡</span>
                  <h2 className="text-lg font-bold text-gray-900">이번주 신규 정책</h2>
                </div>

                <div className="space-y-3">
                  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                    <div className="flex items-start gap-3">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-pink-100 to-pink-200 flex items-center justify-center flex-shrink-0">
                        <span className="text-xl">💰</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="inline-block px-2 py-0.5 bg-pink-50 text-pink-600 rounded text-xs font-semibold">
                            신규
                          </span>
                          <span className="text-xs text-gray-400">2024.03.15</span>
                        </div>
                        <h3 className="font-bold text-gray-900 mb-1 leading-tight">
                          2024년 부모급여 인상
                        </h3>
                        <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                          만 0세 월 100만원, 만 1세 월 50만원으로 인상되었습니다
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                    <div className="flex items-start gap-3">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center flex-shrink-0">
                        <span className="text-xl">🏥</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="inline-block px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-xs font-semibold">
                            인기
                          </span>
                          <span className="text-xs text-gray-400">2024.03.10</span>
                        </div>
                        <h3 className="font-bold text-gray-900 mb-1 leading-tight">
                          어린이 국가예방접종 지원
                        </h3>
                        <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                          만 12세 이하 어린이 필수 예방접종 비용 전액 지원
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                    <div className="flex items-start gap-3">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-100 to-purple-200 flex items-center justify-center flex-shrink-0">
                        <span className="text-xl">🏠</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="inline-block px-2 py-0.5 bg-purple-50 text-purple-600 rounded text-xs font-semibold">
                            신규
                          </span>
                          <span className="text-xs text-gray-400">2024.03.08</span>
                        </div>
                        <h3 className="font-bold text-gray-900 mb-1 leading-tight">
                          신혼부부 특별공급 확대
                        </h3>
                        <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                          자녀가 있는 신혼부부 주택 특별공급 물량 확대
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Popular Posts Section */}
              <div className="px-6 mb-8">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">🔥</span>
                  <h2 className="text-lg font-bold text-gray-900">커뮤니티 인기글</h2>
                  <Link href="/community" className="ml-auto text-sm text-purple-600 font-medium">
                    더보기 →
                  </Link>
                </div>

                <div className="space-y-3">
                  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-pink-50 text-pink-600 rounded text-xs font-semibold">
                        🔥 인기
                      </span>
                      <span className="text-xs text-gray-500">육아 꿀팁</span>
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2 line-clamp-1 leading-snug">
                      어린이집 적응기간 꿀팁 공유합니다
                    </h3>
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 rounded-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center">
                        <span className="text-xs text-white font-semibold">김</span>
                      </div>
                      <span className="text-xs text-gray-500">김민지</span>
                      <span className="text-xs text-gray-400">·</span>
                      <span className="text-xs text-gray-400">1시간 전</span>
                      <div className="flex-1"></div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <MessageSquare className="w-3.5 h-3.5" />
                          <span>24</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-pink-50 text-pink-600 rounded text-xs font-semibold">
                        🔥 인기
                      </span>
                      <span className="text-xs text-gray-500">정책 정보</span>
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2 line-clamp-1 leading-snug">
                      부모급여 신청 방법 정리
                    </h3>
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 rounded-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center">
                        <span className="text-xs text-white font-semibold">이</span>
                      </div>
                      <span className="text-xs text-gray-500">이지은</span>
                      <span className="text-xs text-gray-400">·</span>
                      <span className="text-xs text-gray-400">3시간 전</span>
                      <div className="flex-1"></div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <MessageSquare className="w-3.5 h-3.5" />
                          <span>18</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Category Quick Links */}
              <div className="px-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">📌</span>
                  <h2 className="text-lg font-bold text-gray-900">카테고리</h2>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <Link href="/community?category=tips">
                    <div className="bg-white rounded-xl p-4 border border-gray-100 hover:border-purple-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">💡</div>
                        <div>
                          <h3 className="font-bold text-gray-900 text-sm">육아 꿀팁</h3>
                          <p className="text-xs text-gray-500 mt-0.5">실전 노하우</p>
                        </div>
                      </div>
                    </div>
                  </Link>

                  <Link href="/community?category=policy">
                    <div className="bg-white rounded-xl p-4 border border-gray-100 hover:border-purple-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">📋</div>
                        <div>
                          <h3 className="font-bold text-gray-900 text-sm">정책 정보</h3>
                          <p className="text-xs text-gray-500 mt-0.5">최신 정책</p>
                        </div>
                      </div>
                    </div>
                  </Link>

                  <Link href="/community?category=health">
                    <div className="bg-white rounded-xl p-4 border border-gray-100 hover:border-purple-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">🏥</div>
                        <div>
                          <h3 className="font-bold text-gray-900 text-sm">건강/병원</h3>
                          <p className="text-xs text-gray-500 mt-0.5">건강 관리</p>
                        </div>
                      </div>
                    </div>
                  </Link>

                  <Link href="/community?category=education">
                    <div className="bg-white rounded-xl p-4 border border-gray-100 hover:border-purple-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">🎓</div>
                        <div>
                          <h3 className="font-bold text-gray-900 text-sm">교육/학습</h3>
                          <p className="text-xs text-gray-500 mt-0.5">교육 정보</p>
                        </div>
                      </div>
                    </div>
                  </Link>
                </div>
              </div>

              {/* Bottom Padding */}
              <div className="h-8"></div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
