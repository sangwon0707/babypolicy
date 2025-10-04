"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Heart, Check, X } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useState, useEffect } from "react";

interface Policy {
  id: string;
  title: string;
  description?: string;
  category?: string;
  region?: string;
}

interface UserPolicy {
  policy_id: string;
  is_checked: boolean;
  created_at: string;
  policy: Policy;
}

export default function SavedPoliciesPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [policies, setPolicies] = useState<UserPolicy[]>([]);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchSavedPolicies();
    }
  }, [authLoading, isAuthenticated]);

  const fetchSavedPolicies = async () => {
    try {
      const token = localStorage.getItem("auth_token");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/policies`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch policies");
      }

      const data = await response.json();
      setPolicies(data);
    } catch (error) {
      console.error("Error fetching policies:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCheck = async (policyId: string, currentStatus: boolean) => {
    try {
      const token = localStorage.getItem("auth_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/user/policies/${policyId}/check?is_checked=${!currentStatus}`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update policy status");
      }

      setPolicies(
        policies.map((p) =>
          p.policy_id === policyId ? { ...p, is_checked: !currentStatus } : p
        )
      );
    } catch (error) {
      console.error("Error updating policy status:", error);
      alert("상태 업데이트 중 오류가 발생했습니다.");
    }
  };

  const handleRemovePolicy = async (policyId: string) => {
    if (!confirm("이 정책을 삭제하시겠습니까?")) return;

    try {
      const token = localStorage.getItem("auth_token");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/policies/${policyId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to remove policy");
      }

      setPolicies(policies.filter((p) => p.policy_id !== policyId));
    } catch (error) {
      console.error("Error removing policy:", error);
      alert("정책 삭제 중 오류가 발생했습니다.");
    }
  };

  if (authLoading || loading) {
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

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header - 현재 디자인 스타일 */}
      <div className="bg-gradient-to-br from-pink-400 to-purple-400 px-6 pt-6 pb-8 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Heart className="w-6 h-6" />
            관심 정책
          </h1>
        </div>
        <p className="text-pink-100 text-sm ml-14">
          {policies.length}개의 정책을 저장했어요
        </p>
      </div>

      <div className="px-6 mt-6 space-y-3">
        {policies.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
            <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              저장한 정책이 없어요
            </h3>
            <p className="text-sm text-gray-500">
              AI 챗봇과 대화하며 관심 정책을 저장해보세요!
            </p>
          </div>
        ) : (
          policies.map((item) => (
            <div
              key={item.policy_id}
              className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 hover:border-pink-200 transition-all"
            >
              <div className="flex items-start gap-3">
                <button
                  onClick={() => handleToggleCheck(item.policy_id, item.is_checked)}
                  className={`mt-1 w-6 h-6 rounded-full flex items-center justify-center transition-all ${
                    item.is_checked
                      ? "bg-gradient-to-br from-pink-400 to-purple-400 shadow-md"
                      : "border-2 border-gray-300 hover:border-pink-400"
                  }`}
                >
                  {item.is_checked && <Check className="w-4 h-4 text-white" />}
                </button>

                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800 mb-1">
                    {item.policy?.title || "정책 정보 없음"}
                  </h3>
                  {item.policy?.description && (
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                      {item.policy.description}
                    </p>
                  )}
                  <div className="flex gap-2">
                    {item.policy?.category && (
                      <span className="inline-block px-2 py-1 text-xs font-medium bg-pink-100 text-pink-700 rounded-full">
                        {item.policy.category}
                      </span>
                    )}
                    {item.policy?.region && (
                      <span className="inline-block px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full">
                        {item.policy.region}
                      </span>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => handleRemovePolicy(item.policy_id)}
                  className="p-2 hover:bg-red-50 rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-red-400" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
