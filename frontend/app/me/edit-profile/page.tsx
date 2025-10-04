"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { useState, useEffect } from "react";

export default function EditProfilePage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    gender: "",
    region: "",
    income: "",
    family_size: "",
  });

  useEffect(() => {
    if (user && user.user_profiles) {
      const profile = Array.isArray(user.user_profiles) ? user.user_profiles[0] : user.user_profiles;
      setFormData({
        name: profile?.name || user.name || "",
        gender: profile?.gender || "",
        region: profile?.region || "",
        income: profile?.income?.toString() || "",
        family_size: profile?.family_size?.toString() || "",
      });
    }
  }, [user]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block p-4 bg-white/70 backdrop-blur-sm rounded-full shadow-lg">
            <div className="w-8 h-8 border-4 border-pink-400 border-t-transparent rounded-full animate-spin" />
          </div>
          <p className="mt-4 text-gray-500 text-sm">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    router.push("/login");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem("auth_token");
      const updateData: any = {
        name: formData.name || undefined,
        gender: formData.gender || undefined,
        region: formData.region || undefined,
      };

      if (formData.income) {
        updateData.income = parseInt(formData.income);
      }
      if (formData.family_size) {
        updateData.family_size = parseInt(formData.family_size);
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        throw new Error("Failed to update profile");
      }

      alert("프로필이 업데이트되었습니다!");
      router.push("/me");
    } catch (error) {
      console.error("Error updating profile:", error);
      alert("프로필 업데이트 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header - 현재 디자인 스타일 */}
      <div className="bg-gradient-to-br from-pink-400 to-purple-400 px-6 pt-6 pb-8 shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <h1 className="text-xl font-bold text-white">
            프로필 수정
          </h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="px-6 mt-6 space-y-4">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              이름
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-pink-400 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
              placeholder="이름을 입력하세요"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              성별
            </label>
            <select
              value={formData.gender}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-pink-400 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
            >
              <option value="">선택하세요</option>
              <option value="male">남성</option>
              <option value="female">여성</option>
              <option value="other">기타</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              지역
            </label>
            <input
              type="text"
              value={formData.region}
              onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-pink-400 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
              placeholder="예: 서울시 강남구"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              소득 (만원)
            </label>
            <input
              type="number"
              value={formData.income}
              onChange={(e) => setFormData({ ...formData, income: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-pink-400 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
              placeholder="예: 300"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              가족 구성원 수
            </label>
            <input
              type="number"
              value={formData.family_size}
              onChange={(e) => setFormData({ ...formData, family_size: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-pink-400 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
              placeholder="예: 4"
            />
          </div>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="w-full rounded-2xl bg-gradient-to-r from-pink-400 to-purple-400 hover:from-pink-500 hover:to-purple-500 text-white py-6 text-base font-semibold"
        >
          {loading ? (
            <div className="flex items-center justify-center gap-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              저장 중...
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              <Save className="w-5 h-5" />
              저장하기
            </div>
          )}
        </Button>
      </form>
    </div>
  );
}
