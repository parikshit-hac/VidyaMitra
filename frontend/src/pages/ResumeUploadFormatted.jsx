import { useState } from "react";

import SkillChart from "../components/resume/SkillChart";
import StructuredContentCard from "../components/resume/StructuredContentCard";
import api from "../services/api";
import { analyzeResume, uploadResumeFile, uploadResumeToStorage } from "../services/resumeService";

function ResumeUploadFormatted() {
  const [file, setFile] = useState(null);
  const [targetRole, setTargetRole] = useState("Data Analyst");
  const [loading, setLoading] = useState(false);

  const [storageResult, setStorageResult] = useState(null);
  const [resumeUploadResult, setResumeUploadResult] = useState(null);
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [careerResult, setCareerResult] = useState(null);
  const [error, setError] = useState("");

  const toBase64 = (selectedFile) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(selectedFile);
      reader.onload = () => {
        const result = String(reader.result || "");
        const base64 = result.includes(",") ? result.split(",")[1] : result;
        resolve(base64);
      };
      reader.onerror = reject;
    });

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0] || null;
    if (!selected) {
      setFile(null);
      return;
    }

    if (selected.type !== "application/pdf" && !selected.name.toLowerCase().endsWith(".pdf")) {
      alert("Please upload a PDF file only.");
      event.target.value = "";
      setFile(null);
      return;
    }

    setFile(selected);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file) {
      alert("Please select a PDF file.");
      return;
    }

    setLoading(true);
    setStorageResult(null);
    setResumeUploadResult(null);
    setResumeAnalysis(null);
    setCareerResult(null);
    setError("");

    try {
      const contentBase64 = await toBase64(file);
      const storageResponse = await uploadResumeToStorage({
        filename: file.name,
        content_base64: contentBase64,
        content_type: "application/pdf",
        bucket: "uploads"
      });
      setStorageResult(storageResponse);

      const resumeUploadResponse = await uploadResumeFile(file);
      setResumeUploadResult(resumeUploadResponse);

      const resumeId = resumeUploadResponse?.resume_id;
      if (!resumeId) {
        throw new Error("Resume ID not returned from /resume/upload");
      }

      const analysisResponse = await analyzeResume(resumeId, {
        target_role: targetRole
      });
      setResumeAnalysis(analysisResponse);

      const supportResponse = await api.post("/career/support", {
        goal: `Analyze my resume and provide skill-gap guidance for ${targetRole}`,
        background: "Resume uploaded and analyzed",
        target_role: targetRole,
        constraints: "Provide concise, actionable improvements"
      });
      setCareerResult(supportResponse.data);
    } catch (submissionError) {
      setError(
        submissionError?.response?.data?.detail ||
        submissionError?.message ||
        "Something went wrong while processing your request."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900">Resume Upload & Analysis</h2>
        <p className="mt-1 text-sm text-slate-600">
          Upload your PDF, store it, run backend resume analysis, and generate roadmap guidance.
        </p>

        <form onSubmit={handleSubmit} className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Target Role</label>
            <input
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="e.g. CyberSecurity Engineer"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Resume PDF</label>
            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={handleFileChange}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs"
              required
            />
          </div>

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
            >
              {loading ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Processing...
                </>
              ) : (
                "Upload & Analyze"
              )}
            </button>
          </div>
        </form>
      </div>

      {error ? <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div> : null}

      {storageResult && (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Storage Upload Result</h3>
          <div className="mt-2 grid grid-cols-1 gap-2 text-sm text-slate-700 md:grid-cols-2">
            <p><span className="font-medium">Bucket:</span> {storageResult.bucket}</p>
            <p><span className="font-medium">Path:</span> {storageResult.path}</p>
          </div>
          {storageResult.public_url && (
            <a href={storageResult.public_url} target="_blank" rel="noreferrer" className="mt-3 inline-block text-sm text-brand-700 hover:underline">
              Open Uploaded File
            </a>
          )}
        </div>
      )}

      {resumeUploadResult && (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Resume Module Upload</h3>
          <div className="mt-2 grid grid-cols-1 gap-2 text-sm text-slate-700 md:grid-cols-2">
            <p><span className="font-medium">Resume ID:</span> {resumeUploadResult.resume_id}</p>
            <p><span className="font-medium">Extracted Chars:</span> {resumeUploadResult.extracted_chars}</p>
          </div>
        </div>
      )}

      {resumeAnalysis && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">AI Skill Gap Analysis</h3>
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">Target Role</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{resumeAnalysis.target_role}</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">Identified Skills</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{resumeAnalysis.identified_skills?.length || 0}</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">Skill Gaps</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{resumeAnalysis.skill_gaps?.length || 0}</p>
              </div>
            </div>

            <div className="mt-4 space-y-4">
              <SkillChart title="Identified Skills" items={resumeAnalysis.identified_skills || []} tone="emerald" />
              <SkillChart title="Skill Gaps" items={resumeAnalysis.skill_gaps || []} tone="amber" />
            </div>
          </article>

          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Recommended Courses</h3>
            <ul className="mt-3 space-y-3 text-sm text-slate-700">
              {(resumeAnalysis.recommended_courses || []).map((course, idx) => (
                <li key={`${course.skill}-${idx}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-slate-900">{course.title || course.skill}</p>
                      <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{course.skill || "Skill track"}</p>
                      <p className="mt-2 text-xs text-slate-500">{course.provider || "Provider"}</p>
                    </div>
                  </div>
                  {course.url && (
                    <a href={course.url} target="_blank" rel="noreferrer" className="mt-3 inline-block text-xs font-medium text-brand-700 hover:underline">
                      Open Resource
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </article>
        </div>
      )}

      {resumeAnalysis ? (
        <StructuredContentCard
          title="Resume Summary"
          text={resumeAnalysis.ai_summary}
          source={resumeAnalysis.ai_source || "unknown"}
          accent="emerald"
        />
      ) : null}

      {careerResult && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <StructuredContentCard
            title="Career Support Guidance"
            text={careerResult.ai_guidance}
            source={careerResult.ai_source || "unknown"}
            accent="brand"
          />

          <StructuredContentCard
            title="Roadmap Suggestions"
            text={careerResult.langchain_roadmap}
            source={careerResult.agent_source || "unknown"}
            accent="slate"
          />
        </div>
      )}
    </section>
  );
}

export default ResumeUploadFormatted;
