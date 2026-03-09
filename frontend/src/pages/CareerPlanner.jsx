import { useEffect, useMemo, useState } from "react";

import CertificationCard from "../components/career/CertificationCard";
import RoadmapTimeline from "../components/career/RoadmapTimeline";
import { createCareerPlan, getCareerRoadmaps } from "../services/careerService";

function CareerPlanner() {
  const [form, setForm] = useState({
    target_role: "",
    current_skills: "",
    experience_summary: "",
    resume_summary: "",
    available_hours_per_week: 8,
    timeline_weeks: 12
  });

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [roadmaps, setRoadmaps] = useState([]);

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  useEffect(() => {
    let mounted = true;

    async function loadRoadmaps() {
      setHistoryLoading(true);
      try {
        const data = await getCareerRoadmaps(6);
        if (mounted) {
          setRoadmaps(data);
        }
      } catch (err) {
        if (mounted) {
          setError(err?.response?.data?.detail || "Could not load saved career plans.");
        }
      } finally {
        if (mounted) {
          setHistoryLoading(false);
        }
      }
    }

    loadRoadmaps();
    return () => {
      mounted = false;
    };
  }, []);

  const refreshRoadmaps = async () => {
    const data = await getCareerRoadmaps(6);
    setRoadmaps(data);
  };

  const summary = useMemo(() => {
    if (!result) {
      return "No static starter plan. Submit your own profile to generate a roadmap.";
    }
    return `${result.target_role} • ${result.weekly_plan?.length || 0} weeks • ${result.skill_gaps?.length || 0} gaps`;
  }, [result]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = {
        target_role: form.target_role,
        current_skills: form.current_skills
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        experience_summary: form.experience_summary,
        resume_summary: form.resume_summary,
        available_hours_per_week: Number(form.available_hours_per_week),
        timeline_weeks: Number(form.timeline_weeks)
      };

      const data = await createCareerPlan(payload);
      setResult(data);
      await refreshRoadmaps();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to generate career plan.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Career Planner</h2>
            <p className="mt-1 text-sm text-slate-600">
              Generate a dynamic transition roadmap from your own target role, experience, and available study time.
            </p>
          </div>
          <div className="min-w-44 rounded-xl bg-slate-950 px-4 py-3 text-white">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Planner State</p>
            <p className="mt-2 text-sm text-slate-100">{summary}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          <input
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={form.target_role}
            onChange={(e) => handleChange("target_role", e.target.value)}
            placeholder="Target role, e.g. Business Analyst"
            required
          />
          <input
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={form.current_skills}
            onChange={(e) => handleChange("current_skills", e.target.value)}
            placeholder="Your current skills, comma separated"
            required
          />
          <textarea
            rows={4}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm md:col-span-2"
            value={form.experience_summary}
            onChange={(e) => handleChange("experience_summary", e.target.value)}
            placeholder="Summarize your work, internships, projects, or domain exposure"
          />
          <textarea
            rows={4}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm md:col-span-2"
            value={form.resume_summary}
            onChange={(e) => handleChange("resume_summary", e.target.value)}
            placeholder="Paste a short resume summary or notable achievements"
          />
          <input
            type="number"
            min={1}
            max={80}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={form.available_hours_per_week}
            onChange={(e) => handleChange("available_hours_per_week", e.target.value)}
          />
          <input
            type="number"
            min={4}
            max={52}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={form.timeline_weeks}
            onChange={(e) => handleChange("timeline_weeks", e.target.value)}
          />

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={loading}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
            >
              {loading ? "Generating Plan..." : "Generate Plan"}
            </button>
          </div>
        </form>
      </div>

      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          {result ? (
            <>
          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Skill Gap & Strengths</h3>
            <p className="mt-2 text-sm text-slate-600"><span className="font-medium">Target:</span> {result.target_role}</p>

            <div className="mt-3">
              <p className="mb-1 text-sm font-semibold text-emerald-700">Transferable Strengths</p>
              <div className="flex flex-wrap gap-2">
                {(result.transferable_strengths || []).map((skill) => (
                  <span key={skill} className="rounded-full bg-emerald-50 px-3 py-1 text-xs text-emerald-700">{skill}</span>
                ))}
              </div>
            </div>

            <div className="mt-3">
              <p className="mb-1 text-sm font-semibold text-amber-700">Skill Gaps</p>
              <div className="flex flex-wrap gap-2">
                {(result.skill_gaps || []).map((skill) => (
                  <span key={skill} className="rounded-full bg-amber-50 px-3 py-1 text-xs text-amber-700">{skill}</span>
                ))}
              </div>
            </div>

            <div className="mt-3">
              <p className="mb-1 text-sm font-semibold text-brand-700">Recommended Certifications</p>
              <div className="space-y-2">
                {(result.recommended_certifications || []).map((cert, idx) => (
                  <CertificationCard key={`${cert}-${idx}`} title={cert} />
                ))}
              </div>
            </div>

            <div className="mt-4">
              <p className="mb-2 text-sm font-semibold text-slate-900">Learning Path</p>
              <div className="space-y-3">
                {(result.learning_path || []).map((phase, idx) => (
                  <div key={`${phase.phase}-${idx}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm font-semibold text-slate-900">{phase.phase}</p>
                    <p className="mt-2 text-sm text-slate-700">{(phase.topics || []).join(", ")}</p>
                    {phase.outcome ? <p className="mt-2 text-xs text-slate-500">Outcome: {phase.outcome}</p> : null}
                  </div>
                ))}
              </div>
            </div>
          </article>

          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Weekly Plan</h3>
            <div className="mt-3 max-h-[520px] overflow-auto pr-1">
              <RoadmapTimeline items={result.weekly_plan || []} />
            </div>
            <p className="mt-3 text-xs text-slate-500">{result.notes}</p>
          </article>
            </>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
              No static example plan is shown here anymore. Enter your own role and background to generate a dynamic roadmap.
            </div>
          )}
        </div>

        <aside className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Saved Career Plans</h3>
          <p className="mt-1 text-sm text-slate-600">Recent plans stored by the backend for your account.</p>

          <div className="mt-4 space-y-3">
            {historyLoading ? (
              <div className="flex items-center gap-3 rounded-lg bg-slate-50 px-3 py-4 text-sm text-slate-600">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
                Loading plans...
              </div>
            ) : roadmaps.length ? (
              roadmaps.map((item) => (
                <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-semibold text-slate-900">{item.goal}</p>
                  <p className="mt-2 text-xs text-slate-500">
                    {(item.milestones?.skill_gaps || []).length} gaps • {(item.milestones?.weekly_plan || []).length} weeks
                  </p>
                </div>
              ))
            ) : (
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
                No career plans saved yet.
              </div>
            )}
          </div>
        </aside>
      </div>
    </section>
  );
}

export default CareerPlanner;
