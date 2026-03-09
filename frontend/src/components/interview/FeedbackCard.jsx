function ScorePill({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value ?? 0}</p>
    </div>
  );
}

function FeedbackList({ title, tone, items, bgClass }) {
  return (
    <div>
      <p className={`mb-2 text-sm font-semibold ${tone}`}>{title}</p>
      <div className="space-y-2">
        {(items || []).length ? (
          items.map((item, idx) => (
            <div key={`${title}-${idx}`} className={`rounded-lg px-3 py-2 text-sm text-slate-700 ${bgClass}`}>
              {item}
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-dashed border-slate-200 px-3 py-2 text-sm text-slate-500">
            No items yet.
          </div>
        )}
      </div>
    </div>
  );
}

function FeedbackCard({ feedback }) {
  if (!feedback) {
    return (
      <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">AI Feedback</h3>
        <p className="mt-2 text-sm text-slate-500">Submit an answer to see tone, confidence, accuracy, and guidance.</p>
      </article>
    );
  }

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">AI Feedback</h3>
          <p className="mt-1 text-sm text-slate-600">{feedback.question}</p>
        </div>
        <div className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
          {feedback.status === "completed" ? "Completed" : "In Progress"}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <ScorePill label="Overall" value={feedback.overall_score} />
        <ScorePill label="Tone" value={feedback.tone_score} />
        <ScorePill label="Confidence" value={feedback.confidence_score} />
        <ScorePill label="Accuracy" value={feedback.accuracy_score} />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <FeedbackList title="Strengths" tone="text-emerald-700" items={feedback.strengths} bgClass="bg-emerald-50" />
        <FeedbackList title="Improvements" tone="text-amber-700" items={feedback.improvements} bgClass="bg-amber-50" />
        <FeedbackList
          title="Guidance"
          tone="text-brand-700"
          items={feedback.personalized_guidance}
          bgClass="bg-brand-50"
        />
      </div>
    </article>
  );
}

export default FeedbackCard;
