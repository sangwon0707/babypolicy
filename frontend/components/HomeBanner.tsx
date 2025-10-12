"use client";

import { useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

// 배너 데이터 타입
interface BannerItem {
  id: number;
  title: string;
  description: string;
  image: string; // 실제 이미지 URL
  link?: string;
  bgColor: string; // fallback gradient color
}

// 배너 데이터 - 2025년 10월 기준 주요 육아 정책
const bannerData: BannerItem[] = [
  {
    id: 1,
    title: "💰 부모급여 2배 인상",
    description: "만 0세 월 100만원·만 1세 월 50만원 지급!\n양육 부담을 확실하게 덜어드립니다",
    image: "/banner01.png", // public 폴더에 이미지 추가
    link: "/chat",
    bgColor: "from-pink-400 to-rose-400",
  },
  {
    id: 2,
    title: "🎁 첫만남이용권 200만원",
    description: "출생 시 바로 지급! \n국민행복카드로 유아용품·의류 등 자유롭게 구매하세요",
    image: "/banner02.png",
    link: "/chat",
    bgColor: "from-purple-400 to-indigo-400",
  },
  {
    id: 3,
    title: "👨‍👩‍👧 육아휴직 급여 최대 250만원",
    description: "통상임금 80% 지급! \n엄마·아빠 모두 최대 18개월까지 사용 가능합니다",
    image: "/banner03.png",
    link: "/chat",
    bgColor: "from-blue-400 to-cyan-400",
  },
  {
    id: 4,
    title: "🏫 어린이집 완전 무료",
    description: "0~5세 보육료·유아학비 전액 무료! \n걱정없이 안심하고 맡기세요",
    image: "/banner04.png",
    link: "/chat",
    bgColor: "from-emerald-400 to-teal-400",
  },
  {
    id: 5,
    title: "💉 국가예방접종 전액 지원",
    description: "만 12세까지 필수 예방접종 무료! \n아이 건강을 국가가 책임집니다",
    image: "/banner05.png",
    link: "/chat",
    bgColor: "from-amber-400 to-orange-400",
  },
];

export default function HomeBanner() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  // 다음 슬라이드로 이동
  const nextSlide = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % bannerData.length);
  }, []);

  // 이전 슬라이드로 이동
  const prevSlide = useCallback(() => {
    setCurrentIndex((prev) => (prev - 1 + bannerData.length) % bannerData.length);
  }, []);

  // 특정 슬라이드로 이동
  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  // 자동 슬라이드 (5초마다)
  useEffect(() => {
    if (isPaused) return;

    const interval = setInterval(() => {
      nextSlide();
    }, 5000); // 5초

    return () => clearInterval(interval);
  }, [isPaused, nextSlide]);

  return (
    <div
      className="relative w-full h-48 overflow-hidden rounded-2xl shadow-lg group"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* 슬라이드 컨테이너 */}
      <div
        className="flex h-full transition-transform duration-500 ease-out"
        style={{
          transform: `translateX(-${currentIndex * 100}%)`,
        }}
      >
        {bannerData.map((banner) => (
          <div
            key={banner.id}
            className="w-full h-full flex-shrink-0 relative cursor-pointer"
            onClick={() => banner.link && (window.location.href = banner.link)}
          >
            {/* 배경 이미지 또는 그라데이션 */}
            {banner.image ? (
              <>
                {/* 배경 이미지 with blur */}
                <div
                  className="absolute inset-0 bg-cover bg-center"
                  style={{
                    backgroundImage: `url(${banner.image})`,
                    filter: "blur(8px)",
                    transform: "scale(1.1)", // blur로 인한 가장자리 잘림 방지
                  }}
                />
                {/* 어두운 overlay (텍스트 가독성) */}
                <div className="absolute inset-0 bg-black/40" />
              </>
            ) : (
              /* 이미지가 없을 때 그라데이션 */
              <div
                className={`absolute inset-0 bg-gradient-to-br ${banner.bgColor}`}
              />
            )}

            {/* 배너 컨텐츠 */}
            <div className="relative h-full flex flex-col justify-center px-12 text-white z-10">
              <h3 className="text-xl font-bold mb-2 drop-shadow-lg leading-tight">
                {banner.title}
              </h3>
              <p className="text-sm drop-shadow-md opacity-95 leading-relaxed whitespace-pre-line">
                {banner.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* 좌측 화살표 */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          prevSlide();
        }}
        className="absolute left-2 top-1/2 -translate-y-1/2 w-7 h-7 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full flex items-center justify-center transition-all opacity-0 hover:opacity-100 group-hover:opacity-100"
        aria-label="Previous slide"
      >
        <ChevronLeft className="w-4 h-4 text-white" />
      </button>

      {/* 우측 화살표 */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          nextSlide();
        }}
        className="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full flex items-center justify-center transition-all opacity-0 hover:opacity-100 group-hover:opacity-100"
        aria-label="Next slide"
      >
        <ChevronRight className="w-4 h-4 text-white" />
      </button>

      {/* 인디케이터 dots */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
        {bannerData.map((_, index) => (
          <button
            key={index}
            onClick={(e) => {
              e.stopPropagation();
              goToSlide(index);
            }}
            className={`h-1.5 rounded-full transition-all ${
              index === currentIndex
                ? "bg-white w-5"
                : "bg-white/50 hover:bg-white/70 w-1.5"
            }`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
