"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MessageSquare, Users, User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const navItems = [
  { href: "/", icon: Home, label: "홈" },
  { href: "/chat", icon: MessageSquare, label: "챗봇" },
  { href: "/community", icon: Users, label: "커뮤니티" },
  { href: "/me", icon: User, label: "마이", requiresAuth: true },
];

export default function BottomNav() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-10 mx-auto h-16 w-full max-w-md bg-white/98 backdrop-blur-sm border-t border-gray-200 pb-safe">
      <div className="grid h-full grid-cols-4">
        {navItems.map((item) => {
          // Conditional href: if item requires auth and user is not authenticated, go to login
          const targetHref = item.requiresAuth && !isAuthenticated ? "/login" : item.href;
          // For home page, exact match. For others, startsWith
          const isActive = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={targetHref}
              aria-label={item.label}
              aria-current={isActive ? "page" : undefined}
              className="flex flex-col items-center justify-center gap-1 min-h-[44px] transition-all"
            >
              <item.icon
                className={`h-6 w-6 transition-all ${
                  isActive
                    ? "stroke-purple-600"
                    : "stroke-gray-400"
                }`}
                strokeWidth={isActive ? 2.5 : 2}
                aria-hidden="true"
              />
              <span className={`text-[11px] transition-all ${
                isActive
                  ? "font-semibold text-purple-600"
                  : "font-medium text-gray-500"
              }`}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
