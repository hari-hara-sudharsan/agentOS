"use client"

import Link from "next/link"
import UserProfile from "./UserProfile"
import LogoutButton from "./LogoutButton"

export default function Navbar() {

  return (
    <nav className="flex justify-between items-center px-8 py-6 border-b border-amber-700 bg-slate-900 backdrop-blur-md sticky top-0 z-50 shadow-lg">
      <div className="flex items-center gap-4">
        <h1 className="text-4xl font-bold tracking-widest text-amber-400 uppercase" style={{ fontFamily: 'var(--font-display)' }}>
          AGENTOS
        </h1>
      </div>

      <div className="flex gap-8 items-center text-sm uppercase tracking-widest text-amber-100">
        <Link href="/dashboard" className="hover:text-amber-300 transition-colors duration-300 relative group font-medium">
          Dashboard
          <span className="absolute -bottom-2 left-0 w-0 h-[2px] bg-amber-300 group-hover:w-full transition-all duration-300"></span>
        </Link>
        <Link href="/integrations" className="hover:text-amber-300 transition-colors duration-300 relative group font-medium">
          Integrations
          <span className="absolute -bottom-2 left-0 w-0 h-[2px] bg-amber-300 group-hover:w-full transition-all duration-300"></span>
        </Link>
        <Link href="/activity" className="hover:text-amber-300 transition-colors duration-300 relative group font-medium">
          Activity
          <span className="absolute -bottom-2 left-0 w-0 h-[2px] bg-amber-300 group-hover:w-full transition-all duration-300"></span>
        </Link>
        <Link href="/approvals" className="hover:text-amber-300 transition-colors duration-300 relative group font-medium">
          Approvals
          <span className="absolute -bottom-2 left-0 w-0 h-[2px] bg-amber-300 group-hover:w-full transition-all duration-300"></span>
        </Link>

        <div className="h-6 w-px bg-amber-700 mx-3"></div>

        <UserProfile />
        <LogoutButton />
      </div>
    </nav>
  )

}
