"use client";

import { useState, useEffect } from "react";
import Image from "next/image";

interface Ad {
  id: number;
  image: string;
  title: string;
  originalPrice: number;
  discountRate: number;
  finalPrice: number;
  rating: number;
  reviewCount: number;
  badge?: string;
}

const advertisements: Ad[] = [
  {
    id: 1,
    image: "/advertisement/꿀벌머리쿵쿠션.jpg",
    title: "꿀벌 머리쿵 쿠션",
    originalPrice: 25900,
    discountRate: 38,
    finalPrice: 15810,
    rating: 5.0,
    reviewCount: 1809,
    badge: "미사일배송"
  },
  {
    id: 2,
    image: "/advertisement/젖병소독기.jpg",
    title: "UV 젖병 소독기",
    originalPrice: 89000,
    discountRate: 45,
    finalPrice: 48950,
    rating: 4.8,
    reviewCount: 3421,
    badge: "특가"
  },
  {
    id: 3,
    image: "/advertisement/아기턱받이.jpg",
    title: "실리콘 아기 턱받이",
    originalPrice: 18900,
    discountRate: 32,
    finalPrice: 12852,
    rating: 4.9,
    reviewCount: 2156,
    badge: "미사일배송"
  },
  {
    id: 4,
    image: "/advertisement/하기스기저귀.jpg",
    title: "하기스 기저귀 대용량",
    originalPrice: 45000,
    discountRate: 28,
    finalPrice: 32400,
    rating: 4.7,
    reviewCount: 8934,
    badge: "베스트"
  }
];

export default function HomeAdvertisement() {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % advertisements.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev - 1 + advertisements.length) % advertisements.length);
  };

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % advertisements.length);
  };

  const currentAd = advertisements[currentIndex];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="px-3 py-2 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-orange-100 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="text-base">🎁</span>
          <h3 className="text-xs font-bold text-gray-800">육아 필수템 특가</h3>
        </div>
        <span className="text-[10px] text-gray-500">AD</span>
      </div>

      {/* Ad Content */}
      <div className="relative px-3">
        <div className="flex items-center gap-3 max-w-[420px] mx-auto">
          {/* Image Section */}
          <div className="w-28 flex-shrink-0 relative bg-gray-50">
            <div className="h-24 relative">
              <Image
                src={currentAd.image}
                alt={currentAd.title}
                fill
                className="object-cover"
                sizes="112px"
              />
            </div>
          </div>

          {/* Info Section */}
          <div className="flex-1 p-3">
            {currentAd.badge && (
              <span className="inline-block px-1.5 py-0.5 bg-blue-500 text-white text-[10px] font-bold rounded mb-1.5">
                🚀 {currentAd.badge}
              </span>
            )}
            <h4 className="text-xs font-bold text-gray-900 mb-1 line-clamp-2">
              {currentAd.title}
            </h4>

            <div className="mb-2">
              <div className="text-[11px] text-gray-400 line-through mb-0.5">
                {currentAd.originalPrice.toLocaleString()}원
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-red-500 text-[11px] font-bold">{currentAd.discountRate}%</span>
                <span className="text-sm font-bold text-gray-900">
                  {currentAd.finalPrice.toLocaleString()}원
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <div className="flex">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400 text-[9px]">⭐</span>
                ))}
              </div>
              <span className="text-[10px] text-gray-500">({currentAd.reviewCount.toLocaleString()})</span>
            </div>
          </div>
        </div>

        {/* Navigation Arrows removed for mobile swipe-first UX */}

        {/* Dots Indicator */}
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5 z-10">
          {advertisements.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                index === currentIndex ? "bg-purple-500 w-4" : "bg-gray-300"
              }`}
              aria-label={`${index + 1}번 상품으로 이동`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
