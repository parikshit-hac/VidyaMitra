function RoadmapTimeline({ items }) {
  if (!items?.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
        No weekly roadmap available yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={`week-${item.week}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">Week {item.week}</p>
              <p className="mt-1 text-sm text-slate-700">{item.focus}</p>
              {item.deliverable ? <p className="mt-2 text-xs text-slate-500">Deliverable: {item.deliverable}</p> : null}
            </div>
            <div className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700 shadow-sm">
              {item.hours} hrs
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default RoadmapTimeline;
