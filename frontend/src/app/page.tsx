export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center">
      <h1 className="text-4xl font-bold mb-4 text-indigo-600">AI Career Agent</h1>
      <p className="text-lg text-gray-600 max-w-2xl mb-8">
        Upload your resume, discover skill gaps, get matched with relevant jobs,
        and receive tailored application drafts — all with human-in-the-loop approval.
      </p>
      <div className="flex gap-4">
        <a
          href="/upload"
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
        >
          Get Started
        </a>
        <a
          href="/login"
          className="border border-gray-300 px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition"
        >
          Login
        </a>
      </div>
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-3xl mb-3">📄</div>
          <h3 className="font-semibold mb-2">Resume Analysis</h3>
          <p className="text-sm text-gray-500">Upload PDF/DOCX and get structured parsing + ATS scoring</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-3xl mb-3">🎯</div>
          <h3 className="font-semibold mb-2">Skill Gap Report</h3>
          <p className="text-sm text-gray-500">See exactly what skills you need for your target role</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-3xl mb-3">🤖</div>
          <h3 className="font-semibold mb-2">Smart Recommendations</h3>
          <p className="text-sm text-gray-500">Get project ideas and resources grounded in your gap</p>
        </div>
      </div>
    </div>
  );
}
