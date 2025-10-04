'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  // Redirect to home if already authenticated
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/");
    }
  }, [authLoading, isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      router.push("/");
    } catch (err: any) {
      // Handle different error formats
      let errorMessage = "로그인에 실패했습니다. 다시 시도해주세요.";

      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.detail) {
        errorMessage = err.detail;
      } else if (err?.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-pink-50/30 to-white pb-20">
      {/* Header */}
      <div className="pt-safe">
        <div className="px-6 pt-12 pb-8">
          <div className="inline-block px-3 py-1 bg-pink-100 rounded-full mb-4">
            <span className="text-sm font-medium text-pink-700">👶 육아 정책 도우미</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            로그인
          </h1>
          <p className="text-sm text-gray-500">
            BabyPolicy에 오신 것을 환영합니다
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="flex-1 px-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div role="alert" className="text-sm text-red-600 bg-red-50 px-4 py-3 rounded-lg border border-red-100">
              {error}
            </div>
          )}

          <div>
            <Label htmlFor="email" className="text-sm font-medium text-gray-700 mb-2 block">
              이메일
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              aria-label="이메일 입력"
              className="h-12 bg-white border-gray-200 focus:border-gray-900 focus:ring-gray-900"
            />
          </div>

          <div>
            <Label htmlFor="password" className="text-sm font-medium text-gray-700 mb-2 block">
              비밀번호
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              aria-label="비밀번호 입력"
              className="h-12 bg-white border-gray-200 focus:border-gray-900 focus:ring-gray-900"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            aria-label={loading ? "로그인 중..." : "로그인"}
            className="w-full h-12 bg-gradient-to-r from-pink-400 to-purple-400 text-white font-semibold rounded-lg hover:from-pink-500 hover:to-purple-500 active:from-pink-400 active:to-purple-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-8 shadow-sm"
          >
            {loading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <div className="mt-6 text-center pb-6">
          <Link
            href="/register"
            className="text-sm text-gray-600 hover:text-pink-600 transition-colors"
          >
            계정이 없으신가요? <span className="font-semibold text-pink-600">회원가입</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
