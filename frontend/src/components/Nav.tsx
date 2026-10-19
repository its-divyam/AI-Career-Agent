"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { isLoggedIn, clearToken } from "@/lib/auth";

export default function Nav() {
  const router = useRouter();
  const pathname = usePathname();
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    setLoggedIn(isLoggedIn());
  }, [pathname]);

  function handleLogout() {
    clearToken();
    setLoggedIn(false);
    router.push("/login");
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Image src="/logo.png" alt="Skillgraph" width={36} height={36} className="rounded" />
          <span className="text-xl font-bold text-indigo-900">Skillgraph</span>
        </Link>
        <div className="flex gap-4 text-sm items-center">
          {loggedIn ? (
            <>
              <Link href="/upload" className="hover:text-indigo-600">Upload Resume</Link>
              <Link href="/dashboard" className="hover:text-indigo-600">Dashboard</Link>
              <Link href="/jobs" className="hover:text-indigo-600">Jobs</Link>
              <Link href="/applications" className="hover:text-indigo-600">Applications</Link>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-red-600 ml-2"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-indigo-600">Login</Link>
              <Link href="/register" className="bg-indigo-900 text-white px-3 py-1.5 rounded-lg hover:bg-indigo-800">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
