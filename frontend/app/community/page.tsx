"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { MessageCircle, Eye, Pencil } from "lucide-react";
import { communityApi } from "@/lib/api";

interface Post {
  id: string;
  title: string;
  content: string;
  author: {
    name: string;
  };
  category_id: string;
  created_at: string;
  views_count: number;
  likes_count: number;
  comments_count: number;
}

interface Category {
  id: string;
  label: string;
  color_code?: string;
  icon_emoji?: string;
}

export default function CommunityPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [selectedCategory]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [postsData, categoriesData] = await Promise.all([
        communityApi.getPosts(0, 20, selectedCategory),
        communityApi.getCategories(),
      ]);
      setPosts(postsData);
      setCategories(categoriesData);
    } catch (error) {
      console.error("Failed to load community data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "방금 전";
    if (minutes < 60) return `${minutes}분 전`;
    if (hours < 24) return `${hours}시간 전`;
    if (days < 7) return `${days}일 전`;
    return date.toLocaleDateString("ko-KR");
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-5 py-4 sticky top-0 z-10">
        <h1 className="text-xl font-bold text-gray-900 mb-4">커뮤니티</h1>

        {/* Icon Categories - 2 rows */}
        <div className="overflow-x-auto pb-2 scrollbar-hide">
          <div className="flex gap-3 min-w-max pb-2">
            <button
              onClick={() => setSelectedCategory(undefined)}
              className="flex flex-col items-center gap-1 min-w-[64px]"
            >
              <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all ${
                !selectedCategory ? 'bg-gradient-to-br from-pink-400 to-purple-400' : 'bg-gray-100'
              }`}>
                <span className="text-2xl">🏠</span>
              </div>
              <span className="text-xs font-medium text-gray-700">전체</span>
            </button>

            {categories.slice(0, 9).map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className="flex flex-col items-center gap-1 min-w-[64px]"
              >
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all ${
                  selectedCategory === category.id
                    ? 'bg-gradient-to-br from-pink-400 to-purple-400'
                    : 'bg-gray-100'
                }`}>
                  <span className="text-2xl">{category.icon_emoji || '📌'}</span>
                </div>
                <span className="text-xs font-medium text-gray-700 text-center leading-tight">
                  {category.label}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Section Title */}
      <div className="px-5 py-4 bg-white mt-2">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-bold text-gray-900">다들 이런 얘기하는 중</h2>
          <div className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center">
            <span className="text-xs text-gray-600">ℹ️</span>
          </div>
        </div>
      </div>

      {/* Posts */}
      <div className="bg-white pb-24">
        {isLoading ? (
          <div className="text-center py-16">
            <div className="w-10 h-10 border-4 border-pink-400 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="mt-4 text-gray-500 text-sm">로딩 중...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-16">
            <span className="text-5xl block mb-3">💬</span>
            <p className="text-gray-500">아직 게시글이 없어요</p>
            <p className="text-sm text-gray-400 mt-2">첫 번째 게시글을 작성해보세요!</p>
          </div>
        ) : (
          posts.map((post, index) => (
            <Link key={post.id} href={`/community/${post.id}`}>
              <div className={`px-5 py-4 hover:bg-gray-50 transition-colors ${
                index !== posts.length - 1 ? 'border-b border-gray-100' : ''
              }`}>
                {/* Category Badge */}
                <div className="flex items-center gap-2 mb-2">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-pink-50 text-pink-600 rounded text-xs font-semibold">
                    🔥 인기
                  </span>
                  {post.category_id && (
                    <span className="text-xs text-gray-500">
                      {categories.find(c => c.id === post.category_id)?.label}
                    </span>
                  )}
                </div>

                {/* Title */}
                <h3 className="text-base font-bold text-gray-900 mb-2 line-clamp-2 leading-snug">
                  {post.title}
                </h3>

                {/* Content Preview */}
                <p className="text-sm text-gray-600 mb-3 line-clamp-2 leading-relaxed">
                  {post.content}
                </p>

                {/* Author & Stats */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center">
                      <span className="text-xs text-white font-semibold">
                        {post.author.name?.charAt(0) || '익'}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {post.author.name || "익명"}
                    </span>
                    <span className="text-xs text-gray-400">·</span>
                    <span className="text-xs text-gray-400">{formatDate(post.created_at)}</span>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Eye className="w-3.5 h-3.5" />
                      <span>{formatNumber(post.views_count)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="w-3.5 h-3.5" />
                      <span>{formatNumber(post.comments_count)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>

      {/* Floating Action Button */}
      <Link href="/community/create">
        <button
          aria-label="게시글 작성"
          className="fixed right-5 bottom-24 w-14 h-14 rounded-full bg-gradient-to-br from-teal-400 to-cyan-500 shadow-lg hover:shadow-xl active:scale-95 transition-all flex items-center justify-center z-20"
        >
          <Pencil className="w-6 h-6 text-white" />
        </button>
      </Link>

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
