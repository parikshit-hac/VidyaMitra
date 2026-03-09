function QuestionCard({ item, index, isActive, onSelect }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(index)}
      className={`w-full rounded-xl border px-4 py-3 text-left transition ${
        isActive
          ? "border-brand-300 bg-brand-50 text-brand-900 shadow-sm"
          : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium leading-6">
          {index + 1}. {item.question}
        </p>
        {isActive && <span className="rounded-full bg-brand-600 px-2 py-1 text-[10px] font-semibold text-white">Live</span>}
      </div>
      <p className="mt-2 text-xs uppercase tracking-wide text-slate-500">{item.competency || "General"}</p>
    </button>
  );
}

export default QuestionCard;
