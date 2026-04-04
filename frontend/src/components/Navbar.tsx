"use client"

import Link from "next/link"
import UserProfile from "./UserProfile"
import LogoutButton from "./LogoutButton"

export default function Navbar() {
  return (
    <nav className="grid grid-cols-[auto_1fr_auto] items-center px-4 md:px-8 h-20 border-b border-amber-700 bg-slate-900 backdrop-blur-md sticky top-0 z-50 shadow-lg">

      {/* ── Brand ── */}
      <div className="flex items-center">
        <h1
          className="text-3xl md:text-4xl font-bold tracking-wide text-amber-400 uppercase leading-none"
          style={{ fontFamily: "var(--font-display)" }}
        >
          AGENTOS
        </h1>
      </div>

      {/* ── Center navigation ── */}
      <div className="flex justify-center">
        <div className="flex items-center text-sm md:text-base font-semibold uppercase tracking-normal text-amber-100">
          {[
            { href: "/dashboard",    label: "Dashboard"    },
            { href: "/integrations", label: "Integrations" },
            { href: "/activity",     label: "Activity"     },
            { href: "/approvals",    label: "Approvals"    },
          ].map(({ href, label }, i) => (
            <Link
              key={href}
              href={href}
              className="relative inline-flex items-center px-2 py-1 hover:text-amber-300 transition-colors duration-300"
              style={{ marginRight: i < 3 ? 24 : 0 }}
            >
              {label}
              <span className="absolute -bottom-1 left-0 w-0 h-px bg-amber-300 group-hover:w-full transition-all duration-300" />
            </Link>
          ))}
        </div>

      </div>

      {/* ── User controls ── */}
      <div className="flex items-center gap-3 justify-end">
        <div className="h-5 w-px bg-amber-700 shrink-0" />
        <UserProfile />
        <LogoutButton />
      </div>
    </nav>
  )
}