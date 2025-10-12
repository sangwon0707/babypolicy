'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { register, isAuthenticated, loading: authLoading } = useAuth();
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

    // Validation
    if (password !== confirmPassword) {
      setError("비밀번호가 일치하지 않습니다");
      return;
    }

    if (password.length < 8) {
      setError("비밀번호는 최소 8자 이상이어야 합니다");
      return;
    }

    setLoading(true);

    try {
      await register(email, password, name || undefined);
      router.push("/");
    } catch (err: any) {
      // Handle different error formats
      let errorMessage = "회원가입에 실패했습니다. 다시 시도해 주세요.";

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
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-purple-50/30 to-white pb-20">
      {/* Header */}
      <div className="pt-safe">
        <div className="px-6 pt-12 pb-8">
          <div className="inline-block px-3 py-1 bg-purple-100 rounded-full mb-4">
            <span className="text-sm font-medium text-purple-700">👶 육아 정책 도우미</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            회원가입
          </h1>
          <p className="text-sm text-gray-500">
            BabyPolicy와 함께 시작하세요
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
            <Label htmlFor="name" className="text-sm font-medium text-gray-700 mb-2 block">
              이름 <span className="text-gray-400 text-xs">(선택)</span>
            </Label>
            <Input
              id="name"
              type="text"
              placeholder="이름"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
              aria-label="이름 입력"
              className="h-12 bg-white border-gray-200 focus:border-gray-900 focus:ring-gray-900"
            />
          </div>

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
              placeholder="8자 이상"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              minLength={8}
              aria-label="비밀번호 입력"
              aria-describedby="password-hint"
              className="h-12 bg-white border-gray-200 focus:border-gray-900 focus:ring-gray-900"
            />
            <p id="password-hint" className="text-xs text-gray-500 mt-2">
              최소 8자 이상
            </p>
          </div>

          <div>
            <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700 mb-2 block">
              비밀번호 확인
            </Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="비밀번호 재입력"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={loading}
              aria-label="비밀번호 확인 입력"
              className="h-12 bg-white border-gray-200 focus:border-gray-900 focus:ring-gray-900"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            aria-label={loading ? "회원가입 진행 중..." : "회원가입"}
            className="w-full h-12 bg-gradient-to-r from-purple-400 to-pink-400 text-white font-semibold rounded-lg hover:from-purple-500 hover:to-pink-500 active:from-purple-400 active:to-pink-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-8 shadow-sm"
          >
            {loading ? "가입 중..." : "회원가입"}
          </button>
        </form>

        <div className="mt-6 text-center pb-6">
          <Link
            href="/login"
            className="text-sm text-gray-600 hover:text-purple-600 transition-colors"
          >
            이미 계정이 있으신가요? <span className="font-semibold text-purple-600">로그인</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
