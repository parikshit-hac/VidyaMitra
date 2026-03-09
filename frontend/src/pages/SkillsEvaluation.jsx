import { useEffect, useMemo, useState } from "react";

import api from "../services/api";

function toSkillList(profileData) {
  if (!profileData) return [];
  if (Array.isArray(profileData.skills)) {
    if (typeof profileData.skills[0] === "string") return profileData.skills;
    if (typeof profileData.skills[0] === "object") {
      return profileData.skills.map((s) => s.name || s.skill).filter(Boolean);
    }
  }
  if (profileData.skill_scores && typeof profileData.skill_scores === "object") {
    return Object.keys(profileData.skill_scores);
  }
  return [];
}

function SkillsEvaluation() {
  const [targetRole, setTargetRole] = useState("Data Analyst");
  const [skillInput, setSkillInput] = useState("SQL, Excel, Python");

  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState("");
  const [animated, setAnimated] = useState(false);

  const [result, setResult] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function bootstrap() {
      setInitialLoading(true);
      try {
        const { data } = await api.get("/resources/sync/recent", { params: { limit: 30 } });
        const users = data?.users || [];
        const localUser = (() => {
          try {
            const raw = localStorage.getItem("vm_user");
            return raw ? JSON.parse(raw) : null;
          } catch {
            return null;
          }
        })();

        const current =
          users.find((u) => localUser?.email && u.email === localUser.email) ||
          users.find((u) => localUser?.id && u.id === localUser.id) ||
          users[0] ||
          null;

        const skills = toSkillList(current?.profile_data);
        if (mounted && skills.length > 0) {
          setSkillInput(skills.join(", "));
        }
      } catch {
        // keep defaults
      } finally {
        if (mounted) setInitialLoading(false);
      }
    }

    bootstrap();
    return () => {
      mounted = false;
    };
  }, []);

  const evaluateSkills = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setAnimated(false);

    try {
      const payload = {
        target_role: targetRole,
        current_skills: skillInput
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        years_experience: 1,
        education_level: "bachelor"
      };

      const { data } = await api.post("/evaluate/eligibility", payload);
      setResult(data);
      setTimeout(() => setAnimated(true), 120);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to evaluate skills.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const skillBars = useMemo(() => {
    if (!result) return [];
    if (Array.isArray(result.skill_breakdown) && result.skill_breakdown.length > 0) {
      return result.skill_breakdown.map((s) => ({ name: s.skill, score: Number(s.score) || 0 })).slice(0, 12);
    }
    const matched = (result.matched_skills || []).map((name) => ({ name, score: 85 }));
    const missing = (result.missing_skills || []).map((name) => ({ name, score: 35 }));
    return [...matched, ...missing].slice(0, 10);
  }, [result]);

  const confidenceScore = result?.eligibility_score || 0;
  const confidenceTone = confidenceScore >= 75 ? "text-emerald-700" : confidenceScore >= 60 ? "text-amber-700" : "text-rose-700";

  const improvementAreas = useMemo(() => {
    if (!result) return [];
    if (Array.isArray(result.improvement_areas) && result.improvement_areas.length > 0) {
      return result.improvement_areas.map((area) => ({
        name: area.skill || "Skill",
        tip: area.tip || "Practice with role-specific tasks and project outcomes."
      }));
    }
    return (result.missing_skills || []).slice(0, 4).map((skill) => ({
      name: skill,
      tip: "Improve this skill with weekly focused practice and a mini project."
    }));
  }, [result]);

  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900">Skills Evaluation</h2>
        <p className="mt-1 text-sm text-slate-600">Dynamic role-based evaluation using your skills and target job role.</p>

        <form onSubmit={evaluateSkills} className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          <input
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Target role"
            required
          />
          <input
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Skills (comma separated)"
            required
          />
          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={loading || initialLoading}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
            >
              {loading ? "Evaluating..." : "Evaluate Skills"}
            </button>
          </div>
        </form>

        {error && <p className="mt-3 text-sm text-rose-700">{error}</p>}
      </div>

      {(loading || initialLoading) && (
        <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex items-center justify-center gap-3 text-slate-600">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
            <span className="text-sm">Loading evaluation...</span>
          </div>
        </div>
      )}

      {result && !loading && (
        <>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
              <h3 className="text-lg font-semibold text-slate-900">Role Skill Match</h3>
              <div className="mt-4 space-y-4">
                {skillBars.map((skill) => (
                  <div key={skill.name}>
                    <div className="mb-1 flex items-center justify-between text-sm">
                      <span className="font-medium text-slate-700">{skill.name}</span>
                      <span className="text-slate-500">{skill.score}%</span>
                    </div>
                    <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-brand-500 transition-all duration-1000 ease-out"
                        style={{ width: `${animated ? skill.score : 0}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-900">Confidence Score</h3>
              <p className={`mt-3 text-4xl font-bold ${confidenceTone}`}>{confidenceScore}%</p>
              <p className="mt-2 text-sm text-slate-600">Eligibility for {result.target_role} based on current profile.</p>
              <div className="mt-4 space-y-1 text-xs text-slate-500">
                <p>Skill: {result.criteria_breakdown?.skill_score ?? 0}</p>
                <p>Experience: {result.criteria_breakdown?.experience_score ?? 0}</p>
                <p>Education: {result.criteria_breakdown?.education_bonus ?? 0}</p>
              </div>
            </article>
          </div>

          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Recommended Improvement Areas</h3>
            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
              {improvementAreas.map((area) => (
                <div key={area.name} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-semibold text-slate-800">{area.name}</p>
                  <p className="mt-2 text-sm text-slate-600">{area.tip}</p>
                </div>
              ))}
              {improvementAreas.length === 0 && <p className="text-sm text-slate-500">No critical gaps identified. Keep practicing advanced scenarios.</p>}
            </div>
          </article>
        </>
      )}
    </section>
  );
}

export default SkillsEvaluation;
