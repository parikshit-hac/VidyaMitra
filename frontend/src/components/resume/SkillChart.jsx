function SkillChart({ title, items, tone = "emerald" }) {
  const toneMap = {
    emerald: "bg-emerald-50 text-emerald-700",
    amber: "bg-amber-50 text-amber-700",
    slate: "bg-slate-100 text-slate-700"
  };

  const pillClass = toneMap[tone] || toneMap.slate;

  return (
    <div>
      <p className="mb-2 text-sm font-semibold text-slate-800">{title}</p>
      <div className="flex flex-wrap gap-2">
        {(items || []).length ? (
          items.map((item) => (
            <span key={item} className={`rounded-full px-3 py-1 text-xs font-medium ${pillClass}`}>
              {item}
            </span>
          ))
        ) : (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-500">No data</span>
        )}
      </div>
    </div>
  );
}

export default SkillChart;
