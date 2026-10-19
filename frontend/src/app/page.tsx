import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center">
      <Image
        src="/logo.png"
        alt="Skillgraph"
        width={140}
        height={140}
        className="mb-6 rounded-2xl"
        priority
      />
      <h1 className="text-5xl font-extrabold mb-3 text-indigo-900 tracking-tight">
        Skillgraph
      </h1>
      <p className="text-lg text-gray-500 max-w-xl mb-10">
        Analyze your skills, discover gaps, and match to the right careers —
        powered by AI and grounded in your real experience.
      </p>
      <div className="flex gap-4">
        <Link
          href="/register"
          className="bg-indigo-900 text-white px-8 py-3 rounded-lg font-medium hover:bg-indigo-800 transition"
        >
          Get Started
        </Link>
        <Link
          href="/login"
          className="border border-gray-300 px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition"
        >
          Login
        </Link>
      </div>

      <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl w-full">
        <FeatureCard
          icon="📄"
          title="Resume Analysis"
          description="Upload PDF/DOCX and get structured parsing with ATS compatibility scoring."
        />
        <FeatureCard
          icon="🎯"
          title="Skill Gap Report"
          description="See exactly which skills you have and which you need for your target role."
        />
        <FeatureCard
          icon="🔗"
          title="Job Matching"
          description="Get matched to jobs based on your skill graph, with per-resume scoring."
        />
      </div>

      <div className="mt-16 max-w-3xl w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          <StepCard
            number={1}
            title="Upload your resume"
            description="PDF or DOCX — parsed in seconds with LLM-powered extraction."
          />
          <StepCard
            number={2}
            title="Pick a target role"
            description="AI Engineer, Data Scientist, Backend Engineer, and more."
          />
          <StepCard
            number={3}
            title="See your skill graph"
            description="Visual breakdown of what you have vs. what you need."
          />
          <StepCard
            number={4}
            title="Apply with confidence"
            description="Match to jobs, draft applications, and track your progress."
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="font-semibold mb-2 text-indigo-900">{title}</h3>
      <p className="text-sm text-gray-500">{description}</p>
    </div>
  );
}

function StepCard({
  number,
  title,
  description,
}: {
  number: number;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-4 items-start">
      <div className="flex-shrink-0 w-9 h-9 rounded-full bg-indigo-900 text-white flex items-center justify-center font-bold text-sm">
        {number}
      </div>
      <div>
        <h4 className="font-semibold text-gray-900">{title}</h4>
        <p className="text-sm text-gray-500 mt-1">{description}</p>
      </div>
    </div>
  );
}
