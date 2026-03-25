"use client"

import Link from "next/link"
import UserProfile from "./UserProfile"
import LogoutButton from "./LogoutButton"

export default function Navbar() {

  return (
    <nav className="flex justify-between items-center px-8 py-5 border-b border-[var(--border-red)] bg-black/40 backdrop-blur-md sticky top-0 z-50">
      <div className="flex items-center gap-4">
        <h1 className="text-3xl font-bold tracking-widest text-[#ff2d2d] uppercase" style={{ fontFamily: 'var(--font-display)', textShadow: 'var(--shadow-red)' }}>
          AGENTOS
        </h1>
      </div>

      <div className="flex gap-8 items-center text-sm uppercase tracking-widest text-[var(--white-base)]">
        <Link href="/dashboard" className="hover:text-[var(--red-hot)] transition-colors duration-300 relative group">
          Dashboard
          <span className="absolute -bottom-2 left-0 w-0 h-[2px] bg-[var(--red-hot)] group-hover:w-full transition-all duration-300"></span>
        </Link>
        <Link href="/integrations" className="hover:text-[var(--red-hot)] transition-colors duration-300 relative group">
          Integrations
          <span className="absolute -bottom-2 left-0 w-0 h-[2px] bg-[var(--red-hot)] group-hover:w-full transition-all duration-300"></span>
        </Link>
        <Link href="/activity" className="hover:text-[var(--red-hot)] transition-colors duration-300 relative group">
          Activity
          <span className="absolute -bottom-2 left-0 w-0 h-[2px] bg-[var(--red-hot)] group-hover:w-full transition-all duration-300"></span>
        </Link>

        <div className="h-6 w-px bg-[var(--border-white)] mx-2"></div>

        <UserProfile />
        <LogoutButton />
      </div>
    </nav>
  )

}
