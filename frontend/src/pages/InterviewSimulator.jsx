import { useEffect, useMemo, useState } from "react";

import FeedbackCard from "../components/interview/FeedbackCard";
import QuestionCard from "../components/interview/QuestionCard";
import { createInterviewSession, getInterviewSessions, submitInterviewAnswer } from "../services/interviewService";

function InterviewSimulator() {
  const [role, setRole] = useState("Data Analyst");
  const [experienceLevel, setExperienceLevel] = useState("beginner");
  const [focusAreas, setFocusAreas] = useState("SQL, Communication");

  const [creatingSession, setCreatingSession] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState("");

  const [session, setSession] = useState(null);
  const [recentSessions, setRecentSessions] = useState([]);
  const [selectedQuestionIndex, setSelectedQuestionIndex] = useState(0);
  const [answersByIndex, setAnswersByIndex] = useState({});
  const [feedback, setFeedback] = useState(null);

  const questions = session?.questions || [];
  const selectedQuestion = questions[selectedQuestionIndex] || null;
  const answer = answersByIndex[selectedQuestionIndex] || "";
  const progressPercent = session?.total_questions
    ? Math.round(((session.answered_count || 0) / session.total_questions) * 100)
    : 0;

  const sessionSummary = useMemo(() => {
    if (!session) {
      return "Create a session to generate tailored questions and track multi-question practice.";
    }
    return `${session.answered_count}/${session.total_questions} answered • ${session.experience_level} level`;
  }, [session]);

  useEffect(() => {
    let mounted = true;

    async function loadHistory() {
      setLoadingHistory(true);
      try {
        const data = await getInterviewSessions(6);
        if (mounted) {
          setRecentSessions(data);
        }
      } catch (err) {
        if (mounted) {
          setError(err?.response?.data?.detail || "Could not load interview history.");
        }
      } finally {
        if (mounted) {
          setLoadingHistory(false);
        }
      }
    }

    loadHistory();
    return () => {
      mounted = false;
    };
  }, []);

  const refreshHistory = async () => {
    const data = await getInterviewSessions(6);
    setRecentSessions(data);
  };

  const handleCreateSession = async (event) => {
    event.preventDefault();
    if (!role.trim()) {
      setError("Please enter a job role.");
      return;
    }

    setCreatingSession(true);
    setError("");
    setFeedback(null);

    try {
      const nextSession = await createInterviewSession({
        role: role.trim(),
        experience_level: experienceLevel,
        focus_areas: focusAreas
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        difficulty: "medium"
      });

      setSession(nextSession);
      setSelectedQuestionIndex(nextSession.current_question_index || 0);
      setAnswersByIndex({});
      await refreshHistory();
    } catch (err) {
      setSession(null);
      setError(err?.response?.data?.detail || "Failed to create interview session.");
    } finally {
      setCreatingSession(false);
    }
  };

  const handleSubmitAnswer = async (event) => {
    event.preventDefault();

    if (!session?.session_id || !selectedQuestion) {
      setError("Create an interview session first.");
      return;
    }

    if (answer.trim().length < 20) {
      setError("Please enter a more detailed answer (at least 20 characters).");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const result = await submitInterviewAnswer(session.session_id, {
        answer: answer.trim(),
        question_index: selectedQuestionIndex,
        target_role: role.trim()
      });

      setFeedback(result);
      setSession((current) =>
        current
          ? {
              ...current,
              answered_count: result.answered_count,
              current_question_index: Math.min(result.answered_count, current.total_questions - 1),
              status: result.status
            }
          : current
      );

      if (result.status !== "completed") {
        setSelectedQuestionIndex(Math.min(result.answered_count, (session?.total_questions || 1) - 1));
      }

      await refreshHistory();
    } catch (err) {
      setFeedback(null);
      setError(err?.response?.data?.detail || "Failed to evaluate interview answer.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAnswerChange = (value) => {
    setAnswersByIndex((current) => ({
      ...current,
      [selectedQuestionIndex]: value
    }));
  };

  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Interview Simulator</h2>
            <p className="mt-1 text-sm text-slate-600">
              Start a dynamic AI mock interview session and get per-question feedback on tone, confidence, and accuracy.
            </p>
          </div>
          <div className="min-w-44 rounded-xl bg-slate-950 px-4 py-3 text-white">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Progress</p>
            <p className="mt-2 text-2xl font-semibold">{progressPercent}%</p>
            <p className="mt-1 text-xs text-slate-300">{sessionSummary}</p>
          </div>
        </div>

        <form onSubmit={handleCreateSession} className="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2">
          <input
            value={role}
            onChange={(event) => setRole(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Job role (e.g. Product Analyst)"
            required
          />

          <select
            value={experienceLevel}
            onChange={(event) => setExperienceLevel(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          <input
            value={focusAreas}
            onChange={(event) => setFocusAreas(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm md:col-span-2"
            placeholder="Focus areas (comma separated), e.g. stakeholder management, analytics, SQL"
          />

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={creatingSession}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
            >
              {creatingSession ? "Creating Session..." : "Start Dynamic Interview"}
            </button>
          </div>
        </form>
      </div>

      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">Generated Questions</h3>
                <p className="mt-1 text-sm text-slate-600">
                  Questions are generated fresh for the role and saved to the backend session.
                </p>
              </div>
              {session && (
                <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700">
                  {session.status?.replace("_", " ")}
                </div>
              )}
            </div>

            <div className="mt-4 space-y-3">
              {questions.length ? (
                questions.map((item, index) => (
                  <QuestionCard
                    key={`${item.question}-${index}`}
                    item={item}
                    index={index}
                    isActive={selectedQuestionIndex === index}
                    onSelect={setSelectedQuestionIndex}
                  />
                ))
              ) : (
                <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
                  No active session yet. Start one above to generate dynamic questions.
                </div>
              )}
            </div>
          </article>

          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Submit Your Answer</h3>
            <p className="mt-2 text-sm text-slate-600">
              {selectedQuestion ? selectedQuestion.question : "Choose or generate a question to begin."}
            </p>

            <form onSubmit={handleSubmitAnswer} className="mt-4 space-y-3">
              <textarea
                value={answer}
                onChange={(event) => handleAnswerChange(event.target.value)}
                rows={8}
                placeholder="Type your answer using Situation, Action, and Result."
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                disabled={!selectedQuestion}
                required
              />
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-slate-500">
                  Question {selectedQuestionIndex + 1} of {session?.total_questions || 0}
                </p>
                <button
                  type="submit"
                  disabled={submitting || !selectedQuestion}
                  className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-60"
                >
                  {submitting ? (
                    <>
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      Evaluating...
                    </>
                  ) : (
                    "Evaluate Answer"
                  )}
                </button>
              </div>
            </form>
          </article>

          <FeedbackCard feedback={feedback} />
        </div>

        <aside className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Recent Interview Sessions</h3>
          <p className="mt-1 text-sm text-slate-600">Persisted sessions from the backend for progress tracking.</p>

          <div className="mt-4 space-y-3">
            {loadingHistory ? (
              <div className="flex items-center gap-3 rounded-lg bg-slate-50 px-3 py-4 text-sm text-slate-600">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
                Loading sessions...
              </div>
            ) : recentSessions.length ? (
              recentSessions.map((item) => (
                <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{item.role}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {item.answered_count}/{item.total_questions} answered
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-slate-900">{item.score}</p>
                      <p className="text-[11px] uppercase tracking-wide text-slate-500">{item.status}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
                No interview sessions yet.
              </div>
            )}
          </div>
        </aside>
      </div>
    </section>
  );
}

export default InterviewSimulator;
