"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, Users, User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const navItems = [
  { href: "/chat", icon: MessageSquare, label: "챗봇", emoji: "💬" },
  { href: "/community", icon: Users, label: "커뮤니티", emoji: "👨‍👩‍👧‍👦" },
  { href: "/me", icon: User, label: "마이", emoji: "👤", requiresAuth: true },
];

export default function BottomNav() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();

  // Don't show on auth pages
  if (pathname.startsWith("/login") || pathname.startsWith("/register")) {
    return null;
  }

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-10 mx-auto h-20 w-full max-w-md bg-white/90 backdrop-blur-md border-t border-pink-100 shadow-lg">
      <div className="grid h-full grid-cols-3">
        {navItems.map((item) => {
          // Conditional href: if item requires auth and user is not authenticated, go to login
          const targetHref = item.requiresAuth && !isAuthenticated ? "/login" : item.href;
          const isActive = pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={targetHref}
              className={`flex flex-col items-center justify-center gap-1 text-xs transition-all ${
                isActive
                  ? "text-pink-500 scale-105"
                  : "text-gray-400 hover:text-gray-600"
              }`}
            >
              <div
                className={`flex items-center justify-center w-12 h-12 rounded-2xl transition-all ${
                  isActive
                    ? "bg-gradient-to-br from-pink-400 to-purple-400 shadow-md"
                    : "bg-gray-100"
                }`}
              >
                {isActive ? (
                  <span className="text-2xl">{item.emoji}</span>
                ) : (
                  <item.icon className="h-6 w-6" strokeWidth={1.5} />
                )}
              </div>
              <span className={`font-medium ${isActive ? "font-semibold" : ""}`}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
