"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Heart, Eye, MessageCircle, Send } from "lucide-react";
import { communityApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

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

interface Comment {
  id: string;
  content: string;
  author: {
    name: string;
  };
  created_at: string;
  parent_id: string | null;
}

interface Category {
  id: string;
  label: string;
  icon_emoji?: string;
}

export default function PostDetailPage() {
  const router = useRouter();
  const params = useParams();
  const postId = params?.post_id as string;
  const { isAuthenticated, token } = useAuth();

  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [newComment, setNewComment] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);

  useEffect(() => {
    if (postId) {
      loadData();
    }
  }, [postId]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [postData, commentsData, categoriesData] = await Promise.all([
        communityApi.getPost(postId),
        communityApi.getComments(postId),
        communityApi.getCategories(),
      ]);
      setPost(postData);
      setComments(commentsData);
      setCategories(categoriesData);
    } catch (error) {
      console.error("Failed to load post:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommentSubmit = async () => {
    if (!newComment.trim()) {
      alert("댓글 내용을 입력해주세요.");
      return;
    }

    if (!isAuthenticated || !token) {
      alert("로그인이 필요합니다.");
      router.push("/login");
      return;
    }

    setIsSubmittingComment(true);
    try {
      await communityApi.createComment(postId, newComment.trim(), null, token);
      setNewComment("");
      // Reload comments
      const commentsData = await communityApi.getComments(postId);
      setComments(commentsData);
    } catch (error) {
      console.error("Failed to create comment:", error);
      alert("댓글 작성에 실패했습니다.");
    } finally {
      setIsSubmittingComment(false);
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

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-pink-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-gray-500 text-sm">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <span className="text-5xl block mb-3">😢</span>
          <p className="text-gray-700 font-medium mb-2">게시글을 찾을 수 없습니다</p>
          <button
            onClick={() => router.push("/community")}
            className="text-pink-500 text-sm hover:underline"
          >
            커뮤니티로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  const category = categories.find((c) => c.id === post.category_id);

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="flex items-center gap-3 px-5 py-4">
          <button
            onClick={() => router.back()}
            className="p-2 -ml-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-700" />
          </button>
          <h1 className="text-lg font-bold text-gray-900">게시글</h1>
        </div>
      </div>

      {/* Post Content */}
      <div className="bg-white px-5 py-6 mb-2">
        {/* Category Badge */}
        {category && (
          <div className="flex items-center gap-2 mb-3">
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-pink-50 text-pink-600 rounded-full text-xs font-semibold">
              {category.icon_emoji} {category.label}
            </span>
          </div>
        )}

        {/* Title */}
        <h2 className="text-xl font-bold text-gray-900 mb-4 leading-snug">
          {post.title}
        </h2>

        {/* Author & Date */}
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center">
            <span className="text-sm text-white font-semibold">
              {post.author.name?.charAt(0) || "익"}
            </span>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">
              {post.author.name || "익명"}
            </p>
            <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
          </div>
        </div>

        {/* Content */}
        <div className="prose prose-sm max-w-none mb-4">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {post.content}
          </p>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 pt-4 border-t border-gray-100">
          <div className="flex items-center gap-1.5 text-gray-500">
            <Eye className="w-4 h-4" />
            <span className="text-sm">{post.views_count}</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <Heart className="w-4 h-4" />
            <span className="text-sm">{post.likes_count}</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <MessageCircle className="w-4 h-4" />
            <span className="text-sm">{post.comments_count}</span>
          </div>
        </div>
      </div>

      {/* Comments Section */}
      <div className="bg-white px-5 py-4">
        <h3 className="text-base font-bold text-gray-900 mb-4">
          댓글 {comments.length}개
        </h3>

        {/* Comments List */}
        <div className="space-y-4 mb-4">
          {comments.length === 0 ? (
            <div className="text-center py-8">
              <span className="text-3xl block mb-2">💬</span>
              <p className="text-gray-500 text-sm">첫 댓글을 작성해보세요!</p>
            </div>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-300 to-cyan-300 flex items-center justify-center flex-shrink-0">
                  <span className="text-xs text-white font-semibold">
                    {comment.author.name?.charAt(0) || "익"}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      {comment.author.name || "익명"}
                    </span>
                    <span className="text-xs text-gray-400">
                      {formatDate(comment.created_at)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {comment.content}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Comment Input */}
        <div className="border-t border-gray-100 pt-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter" && !isSubmittingComment) {
                  handleCommentSubmit();
                }
              }}
              placeholder={
                isAuthenticated
                  ? "댓글을 입력하세요..."
                  : "로그인 후 댓글을 작성할 수 있습니다"
              }
              disabled={!isAuthenticated || isSubmittingComment}
              className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleCommentSubmit}
              disabled={!isAuthenticated || !newComment.trim() || isSubmittingComment}
              className={`px-4 py-2.5 rounded-xl font-medium transition-all ${
                !isAuthenticated || !newComment.trim() || isSubmittingComment
                  ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-pink-400 to-purple-400 text-white hover:shadow-md"
              }`}
            >
              {isSubmittingComment ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
