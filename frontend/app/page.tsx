"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { MessageSquare, Users, Sparkles, Baby } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import HomeBanner from "@/components/HomeBanner";
import HomeAdvertisement from "@/components/HomeAdvertisement";
import { communityApi } from "@/lib/api";

export default function Home() {
  const { user, isAuthenticated, loading } = useAuth();
  const [popularPosts, setPopularPosts] = useState<any[]>([]);
  const [postsLoading, setPostsLoading] = useState(true);

  useEffect(() => {
    const fetchPopularPosts = async () => {
      if (!isAuthenticated) return;

      try {
        const posts = await communityApi.getPopularPosts(2);
        setPopularPosts(posts);
      } catch (error) {
        console.error("Failed to fetch popular posts:", error);
      } finally {
        setPostsLoading(false);
      }
    };

    fetchPopularPosts();
  }, [isAuthenticated]);

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
            <div className="pb-16 bg-gray-50">
              {/* Hero Section */}
              <div className="bg-gradient-to-br from-pink-400 to-purple-400 px-4 pt-8 pb-5">
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

              {/* Auto-slide Policy Banner */}
              <div className="px-4 mt-3 mb-3">
                <HomeBanner />
              </div>

              {/* Popular Posts Section */}
              <div className="px-4 mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">🔥</span>
                  <h2 className="text-lg font-bold text-gray-900">커뮤니티 인기글</h2>
                  <Link href="/community" className="ml-auto text-sm text-purple-600 font-medium">
                    더보기 →
                  </Link>
                </div>

                {postsLoading ? (
                  <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 text-center">
                    <div className="w-8 h-8 border-4 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                    <p className="text-sm text-gray-500">인기글 불러오는 중...</p>
                  </div>
                ) : popularPosts.length === 0 ? (
                  <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 text-center">
                    <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-500 mb-1">아직 게시글이 없습니다</p>
                    <p className="text-xs text-gray-400">첫 번째 글을 작성해보세요!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {popularPosts.map((post) => {
                      const authorName = post.author?.name || post.author?.email?.split('@')[0] || '익명';
                      const authorInitial = authorName[0];
                      const timeAgo = new Date(post.created_at).toLocaleDateString('ko-KR');

                      return (
                        <Link key={post.id} href={`/community/${post.id}`} className="block">
                          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:border-purple-200 transition-colors cursor-pointer">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-pink-50 text-pink-600 rounded text-xs font-semibold">
                                🔥 인기
                              </span>
                              <span className="text-xs text-gray-500">조회수 {post.views_count || 0}</span>
                            </div>
                            <h3 className="font-bold text-gray-900 mb-2 line-clamp-1 leading-snug">
                              {post.title}
                            </h3>
                            <div className="flex items-center gap-2">
                              <div className="w-5 h-5 rounded-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center">
                                <span className="text-xs text-white font-semibold">{authorInitial}</span>
                              </div>
                              <span className="text-xs text-gray-500">{authorName}</span>
                              <span className="text-xs text-gray-400">·</span>
                              <span className="text-xs text-gray-400">{timeAgo}</span>
                              <div className="flex-1"></div>
                              <div className="flex items-center gap-3 text-xs text-gray-500">
                                <div className="flex items-center gap-1">
                                  <MessageSquare className="w-3.5 h-3.5" />
                                  <span>{post.comments_count || 0}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Advertisement Section */}
              <div className="px-6 mb-8">
                <HomeAdvertisement />
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
