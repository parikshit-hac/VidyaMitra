import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import DashboardCard from "../components/dashboard/DashboardCard";
import api from "../services/api";

const cards = [
  {
    icon: "CS",
    title: "Career Support",
    description: "Get guided career paths, transition planning, and role-specific recommendations.",
    to: "/career-support"
  },
  {
    icon: "RA",
    title: "Resume Analysis",
    description: "Upload and analyze resumes for skill gaps, strengths, and actionable improvements.",
    to: "/resume-analysis"
  },
  {
    icon: "SE",
    title: "Skills Evaluation",
    description: "Assess your eligibility and skill readiness for your target role.",
    to: "/skills-evaluation"
  },
  {
    icon: "DQ",
    title: "Dynamic Quiz",
    description: "Generate AI-powered quizzes and track your quiz performance history.",
    to: "/dynamic-quiz"
  },
  {
    icon: "LR",
    title: "Learning Resources",
    description: "Find curated learning resources, courses, and visual aids for upskilling.",
    to: "/learning-resources"
  },
  {
    icon: "IS",
    title: "Interview Simulator",
    description: "Practice mock interviews and receive feedback on confidence and accuracy.",
    to: "/interview-simulator"
  },
  {
    icon: "MI",
    title: "Market Insights",
    description: "Track relevant news and market updates aligned to your career goals.",
    to: "/market-insights"
  }
];

function MetricCard({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function Dashboard() {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadProgress() {
      setLoading(true);
      setError("");
      try {
        const { data } = await api.get("/progress/dashboard");
        if (mounted) setProgress(data);
      } catch (err) {
        if (mounted) {
          setError(err?.response?.data?.detail || "Could not load progress stats.");
          setProgress(null);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadProgress();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <section>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Welcome to VidyaMitra</h2>
        <p className="text-sm text-slate-600">Choose a module to continue your career growth journey.</p>
      </div>

      {loading ? (
        <div className="mb-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
            Loading progress...
          </div>
        </div>
      ) : error ? (
        <div className="mb-5 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">{error}</div>
      ) : (
        <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-6">
          <MetricCard label="Completion" value={`${progress?.summary?.overall_completion_percent ?? 0}%`} />
          <MetricCard label="Resumes" value={progress?.summary?.resume_count ?? 0} />
          <MetricCard label="Interviews" value={progress?.summary?.interview_sessions ?? 0} />
          <MetricCard label="Roadmaps" value={progress?.summary?.roadmaps ?? 0} />
          <MetricCard
            label="Quiz Avg"
            value={`${Math.round(progress?.scores?.average_quiz_percent ?? 0)}%`}
          />
          <MetricCard
            label="Skill Avg"
            value={Math.round(progress?.scores?.average_skill_score ?? 0)}
          />
        </div>
      )}

      <div className="mb-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Quick Actions</h3>
        <p className="mt-1 text-sm text-slate-600">Jump directly into key tasks.</p>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <button
            onClick={() => navigate("/resume-analysis")}
            className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-left transition hover:border-brand-200 hover:bg-brand-50"
          >
            <p className="text-sm font-semibold text-slate-900">Upload Resume</p>
            <p className="mt-1 text-xs text-slate-500">Run resume parsing and skill gap analysis.</p>
          </button>
          <button
            onClick={() => navigate("/career-support")}
            className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-left transition hover:border-brand-200 hover:bg-brand-50"
          >
            <p className="text-sm font-semibold text-slate-900">Create Career Plan</p>
            <p className="mt-1 text-xs text-slate-500">Generate personalized roadmap and weekly steps.</p>
          </button>
          <button
            onClick={() => navigate("/interview-simulator")}
            className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-left transition hover:border-brand-200 hover:bg-brand-50"
          >
            <p className="text-sm font-semibold text-slate-900">Start Mock Interview</p>
            <p className="mt-1 text-xs text-slate-500">Practice Q&A and get structured feedback.</p>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <DashboardCard key={card.title} {...card} />
        ))}
      </div>
    </section>
  );
}

export default Dashboard;
