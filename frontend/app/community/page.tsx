"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, MessageCircle, Heart, Eye, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50/30 to-pink-50/30 pb-20">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-purple-100 p-4 sticky top-0 z-10 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <span className="text-2xl">👨‍👩‍👧‍👦</span>
              우리들의 이야기
            </h1>
            <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
              <Sparkles className="w-3 h-3" />
              육아 경험을 나눠요
            </p>
          </div>
          <Link href="/community/create">
            <Button className="rounded-2xl bg-gradient-to-r from-purple-400 to-pink-400 hover:from-purple-500 hover:to-pink-500 shadow-md">
              <Plus className="w-5 h-5 mr-1" />
              글쓰기
            </Button>
          </Link>
        </div>

        {/* Categories */}
        <div className="flex gap-2 mt-4 overflow-x-auto pb-2 scrollbar-hide">
          <button
            onClick={() => setSelectedCategory(undefined)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all whitespace-nowrap ${
              !selectedCategory
                ? "bg-gradient-to-r from-purple-400 to-pink-400 text-white shadow-md"
                : "bg-white/70 text-gray-600 hover:bg-white"
            }`}
          >
            전체
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all whitespace-nowrap ${
                selectedCategory === category.id
                  ? "bg-gradient-to-r from-purple-400 to-pink-400 text-white shadow-md"
                  : "bg-white/70 text-gray-600 hover:bg-white"
              }`}
            >
              {category.icon_emoji} {category.label}
            </button>
          ))}
        </div>
      </div>

      {/* Posts */}
      <div className="p-4 space-y-3">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block p-4 bg-white/70 backdrop-blur-sm rounded-full shadow-lg">
              <div className="w-8 h-8 border-4 border-pink-400 border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="mt-4 text-gray-500 text-sm">로딩 중...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12 bg-white/70 backdrop-blur-sm rounded-2xl shadow-sm">
            <span className="text-5xl block mb-4">💬</span>
            <p className="text-gray-500">아직 게시글이 없어요</p>
            <p className="text-sm text-gray-400 mt-2">첫 번째 게시글을 작성해보세요!</p>
          </div>
        ) : (
          posts.map((post) => (
            <Link key={post.id} href={`/community/${post.id}`}>
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-sm hover:shadow-md transition-all border border-purple-100 hover:border-purple-300">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">
                      {post.title}
                    </h3>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                      {post.content}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="font-medium text-purple-600">
                        {post.author.name || "익명"}
                      </span>
                      <span>{formatDate(post.created_at)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    {post.views_count}
                  </div>
                  <div className="flex items-center gap-1">
                    <Heart className="w-4 h-4" />
                    {post.likes_count}
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageCircle className="w-4 h-4" />
                    {post.comments_count}
                  </div>
                </div>
              </div>
            </Link>
          ))
        )}
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
