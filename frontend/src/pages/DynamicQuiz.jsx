import { useEffect, useState } from "react";

import { generateQuiz, getQuizHistory, submitQuiz } from "../services/quizService";

function DynamicQuiz() {
  const [topic, setTopic] = useState("CyberSecurity");
  const [level, setLevel] = useState("beginner");
  const [numQuestions, setNumQuestions] = useState(5);

  const [loadingQuiz, setLoadingQuiz] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState("");

  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    let mounted = true;

    async function loadHistory() {
      setLoadingHistory(true);
      try {
        const data = await getQuizHistory(6);
        if (mounted) {
          setHistory(data);
        }
      } catch (err) {
        if (mounted) {
          setError(err?.response?.data?.detail || "Could not load quiz history.");
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
    const data = await getQuizHistory(6);
    setHistory(data);
  };

  const handleGenerateQuiz = async (event) => {
    event.preventDefault();
    setLoadingQuiz(true);
    setError("");
    setResult(null);

    try {
      const data = await generateQuiz({
        topic: topic.trim(),
        level,
        num_questions: Number(numQuestions)
      });
      setQuiz(data);
      setAnswers({});
    } catch (err) {
      setQuiz(null);
      setError(err?.response?.data?.detail || "Failed to generate quiz.");
    } finally {
      setLoadingQuiz(false);
    }
  };

  const handleAnswerChange = (questionId, optionIndex) => {
    setAnswers((current) => ({
      ...current,
      [questionId]: optionIndex
    }));
  };

  const handleSubmitQuiz = async (event) => {
    event.preventDefault();
    if (!quiz?.questions?.length) {
      setError("Generate a quiz first.");
      return;
    }

    const userAnswers = quiz.questions.map((question) =>
      Number.isInteger(answers[question.id]) ? answers[question.id] : -1
    );

    setSubmitting(true);
    setError("");

    try {
      const data = await submitQuiz({
        topic: quiz.topic,
        level: quiz.level,
        questions: quiz.questions,
        user_answers: userAnswers
      });
      setResult(data);
      await refreshHistory();
    } catch (err) {
      setResult(null);
      setError(err?.response?.data?.detail || "Failed to submit quiz.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Dynamic Quiz</h2>
            <p className="mt-1 text-sm text-slate-600">
              Generate a role-specific MCQ quiz from the backend and submit it for scoring and feedback.
            </p>
          </div>
          <div className="min-w-44 rounded-xl bg-slate-950 px-4 py-3 text-white">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Quiz State</p>
            <p className="mt-2 text-sm text-slate-100">
              {quiz?.questions?.length ? `${quiz.questions.length} questions ready` : "No active quiz"}
            </p>
          </div>
        </div>

        <form onSubmit={handleGenerateQuiz} className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Quiz topic, e.g. Data Analysis"
            required
          />

          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          <input
            type="number"
            min={3}
            max={10}
            value={numQuestions}
            onChange={(e) => setNumQuestions(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />

          <div className="md:col-span-3">
            <button
              type="submit"
              disabled={loadingQuiz}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
            >
              {loadingQuiz ? "Generating Quiz..." : "Generate Dynamic Quiz"}
            </button>
          </div>
        </form>
      </div>

      {error ? <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div> : null}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          {quiz?.questions?.length ? (
            <form onSubmit={handleSubmitQuiz} className="space-y-4">
              {quiz.questions.map((question, index) => (
                <article key={question.id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-semibold text-slate-900">
                    {index + 1}. {question.question}
                  </p>
                  <div className="mt-4 space-y-2">
                    {question.options.map((option, optionIndex) => (
                      <label
                        key={`${question.id}-${optionIndex}`}
                        className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-3 text-sm transition ${
                          answers[question.id] === optionIndex
                            ? "border-brand-300 bg-brand-50 text-brand-900"
                            : "border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300"
                        }`}
                      >
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          checked={answers[question.id] === optionIndex}
                          onChange={() => handleAnswerChange(question.id, optionIndex)}
                          className="mt-1"
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </article>
              ))}

              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-60"
              >
                {submitting ? "Submitting..." : "Submit Quiz"}
              </button>
            </form>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
              Generate a quiz to start answering questions.
            </div>
          )}

          {result ? (
            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-900">Quiz Result</h3>
              <div className="mt-4 grid grid-cols-3 gap-3">
                <div className="rounded-lg bg-slate-50 p-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Score</p>
                  <p className="mt-1 text-xl font-bold text-slate-900">{result.score}</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Max</p>
                  <p className="mt-1 text-xl font-bold text-slate-900">{result.max_score}</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Percent</p>
                  <p className="mt-1 text-xl font-bold text-slate-900">{result.percentage}%</p>
                </div>
              </div>

              <div className="mt-4">
                <p className="mb-2 text-sm font-semibold text-slate-900">Feedback</p>
                <div className="space-y-2">
                  {(result.feedback || []).map((item, index) => (
                    <div key={`${item}-${index}`} className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-700">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </article>
          ) : null}
        </div>

        <aside className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900">Recent Quiz History</h3>
          <p className="mt-1 text-sm text-slate-600">Saved quiz attempts returned by the backend.</p>

          <div className="mt-4 space-y-3">
            {loadingHistory ? (
              <div className="flex items-center gap-3 rounded-lg bg-slate-50 px-3 py-4 text-sm text-slate-600">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
                Loading quiz history...
              </div>
            ) : history.length ? (
              history.map((item) => (
                <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        Score {item.score}/{item.max_score}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-slate-900">{item.percentage}%</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
                No quiz attempts yet.
              </div>
            )}
          </div>
        </aside>
      </div>
    </section>
  );
}

export default DynamicQuiz;
