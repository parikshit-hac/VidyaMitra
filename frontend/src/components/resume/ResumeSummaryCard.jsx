function ResumeSummaryCard({ title, lines, source }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <div className="mt-4 space-y-2">
        {(lines || []).length ? (
          lines.map((line, index) => (
            <div key={`${line}-${index}`} className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-700">
              {line}
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500">
            No summary returned.
          </div>
        )}
      </div>
      {source ? <p className="mt-4 text-xs text-slate-500">Source: {source}</p> : null}
    </article>
  );
}

export default ResumeSummaryCard;
