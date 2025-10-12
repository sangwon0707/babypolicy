"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Send } from "lucide-react";
import { communityApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

interface Category {
  id: string;
  label: string;
  color_code?: string;
  icon_emoji?: string;
}

export default function CreatePostPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading, token } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      alert("로그인이 필요합니다.");
      router.push("/login");
      return;
    }
    loadCategories();
  }, [isAuthenticated, authLoading, router]);

  const loadCategories = async () => {
    try {
      const data = await communityApi.getCategories();
      setCategories(data);
    } catch (error) {
      console.error("Failed to load categories:", error);
    } finally {
      setLoadingCategories(false);
    }
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      alert("제목을 입력해주세요.");
      return;
    }
    if (!content.trim()) {
      alert("내용을 입력해주세요.");
      return;
    }
    if (!selectedCategory) {
      alert("카테고리를 선택해주세요.");
      return;
    }

    if (!token) {
      alert("로그인이 필요합니다.");
      router.push("/login");
      return;
    }

    setIsSubmitting(true);
    try {
      await communityApi.createPost(
        title.trim(),
        content.trim(),
        selectedCategory,
        token
      );
      alert("게시글이 작성되었습니다!");
      router.push("/community");
    } catch (error) {
      console.error("Failed to create post:", error);
      alert("게시글 작성에 실패했습니다. 다시 시도해주세요.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading || loadingCategories) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-pink-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-gray-500 text-sm">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="flex items-center justify-between px-5 py-4">
          <button
            onClick={() => router.back()}
            className="p-2 -ml-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-700" />
          </button>
          <h1 className="text-lg font-bold text-gray-900">글쓰기</h1>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !title.trim() || !content.trim() || !selectedCategory}
            className={`px-4 py-2 rounded-full font-semibold transition-all ${
              isSubmitting || !title.trim() || !content.trim() || !selectedCategory
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-gradient-to-r from-pink-400 to-purple-400 text-white hover:shadow-md"
            }`}
          >
            {isSubmitting ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>작성중...</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Send className="w-4 h-4" />
                <span>완료</span>
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Category Selection */}
      <div className="bg-white px-5 py-4 mb-2">
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          카테고리 선택 <span className="text-pink-500">*</span>
        </label>
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-full font-medium transition-all ${
                selectedCategory === category.id
                  ? "bg-gradient-to-r from-pink-400 to-purple-400 text-white shadow-md"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <span className="text-base">{category.icon_emoji || "📌"}</span>
              <span className="text-sm">{category.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Title Input */}
      <div className="bg-white px-5 py-4 mb-2">
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          제목 <span className="text-pink-500">*</span>
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="제목을 입력하세요"
          maxLength={100}
          className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-transparent transition-all"
        />
        <div className="flex justify-end mt-2">
          <span className="text-xs text-gray-400">{title.length}/100</span>
        </div>
      </div>

      {/* Content Input */}
      <div className="bg-white px-5 py-4">
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          내용 <span className="text-pink-500">*</span>
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="여러분의 이야기를 들려주세요&#10;&#10;• 육아 꿀팁이나 경험 공유&#10;• 정책 신청 후기&#10;• 궁금한 점 질문&#10;• 서로 응원하는 따뜻한 커뮤니티를 만들어가요 💕"
          maxLength={2000}
          rows={12}
          className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-transparent transition-all resize-none"
        />
        <div className="flex justify-end mt-2">
          <span className="text-xs text-gray-400">{content.length}/2000</span>
        </div>
      </div>

      {/* Tips Section */}
      <div className="px-5 py-4 mt-2">
        <div className="bg-gradient-to-br from-pink-50 to-purple-50 rounded-2xl p-4 border border-pink-100">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white flex items-center justify-center">
              <span className="text-lg">💡</span>
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-bold text-gray-900 mb-2">글쓰기 팁</h3>
              <ul className="text-xs text-gray-600 space-y-1">
                <li>• 다른 분들이 이해하기 쉽게 구체적으로 작성해주세요</li>
                <li>• 개인정보(이름, 전화번호 등)는 작성하지 마세요</li>
                <li>• 서로 존중하고 배려하는 댓글 문화를 만들어요</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
