import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Career Agent",
  description: "AI-powered career assistant for skill gap analysis and job matching",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <nav className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-indigo-600">
              AI Career Agent
            </a>
            <div className="flex gap-4 text-sm">
              <a href="/upload" className="hover:text-indigo-600">Upload Resume</a>
              <a href="/dashboard" className="hover:text-indigo-600">Dashboard</a>
              <a href="/profile" className="hover:text-indigo-600">Profile</a>
              <a href="/login" className="hover:text-indigo-600">Login</a>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
