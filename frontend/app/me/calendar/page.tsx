"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Calendar as CalendarIcon, ArrowLeft, Trash2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { calendarApi } from "@/lib/api";

export default function CalendarListPage() {
  const { isAuthenticated, token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && isAuthenticated && token) {
      (async () => {
        try {
          const data = await calendarApi.getEvents(token);
          // Sort by date ascending
          const sorted = [...data].sort(
            (a, b) => new Date(a.event_date).getTime() - new Date(b.event_date).getTime()
          );
          setEvents(sorted);
        } catch (e) {
          console.error("Failed to fetch calendar events:", e);
        } finally {
          setLoading(false);
        }
      })();
    } else if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, token, router]);

  const handleDelete = async (eventId: number) => {
    if (!token) return;
    try {
      await calendarApi.deleteEvent(eventId, token);
      setEvents(prev => prev.filter(e => e.id !== eventId));
    } catch (e) {
      console.error("Failed to delete event:", e);
    }
  };

  const getDaysUntil = (dateStr: string) => {
    const now = new Date();
    const d = new Date(dateStr);
    const diff = d.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block p-4 bg-white/70 backdrop-blur-sm rounded-full shadow-lg">
            <div className="w-8 h-8 border-4 border-purple-400 border-t-transparent rounded-full animate-spin" />
          </div>
          <p className="mt-4 text-gray-500 text-sm">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="bg-gradient-to-br from-pink-400 to-purple-400 px-6 pt-6 pb-8 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <button onClick={() => router.back()} className="p-2 hover:bg-white/20 rounded-full transition-colors">
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <CalendarIcon className="w-6 h-6" /> 전체 캘린더 일정
          </h1>
        </div>
        <p className="text-pink-100 text-sm ml-14">모든 일정 보기 및 관리</p>
      </div>

      <div className="px-6 mt-6 space-y-2">
        {events.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
            <CalendarIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">등록된 일정이 없습니다</p>
          </div>
        ) : (
          events.map(event => {
            const daysUntil = getDaysUntil(event.event_date);
            const isPast = daysUntil < 0;
            const isToday = daysUntil === 0;
            return (
              <div
                key={event.id}
                className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center gap-3 group"
              >
                <div className="flex-shrink-0">
                  <div className={`text-white rounded-xl px-3 py-2 text-center min-w-[60px] ${
                    isPast ? 'bg-gray-400' :
                    isToday ? 'bg-gradient-to-br from-green-400 to-emerald-400' :
                    'bg-gradient-to-br from-purple-400 to-pink-400'
                  }`}>
                    <p className="text-xs font-medium">
                      {isPast ? `D+${Math.abs(daysUntil)}` : isToday ? 'D-Day' : `D-${daysUntil}`}
                    </p>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 truncate">{event.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {new Date(event.event_date).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
                  </p>
                  {event.description && (
                    <p className="text-xs text-gray-400 mt-1 line-clamp-1">{event.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(event.id)}
                  className="flex-shrink-0 p-2 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                  aria-label="일정 삭제"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

