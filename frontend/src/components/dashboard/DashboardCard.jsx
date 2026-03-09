import { Link } from "react-router-dom";

function DashboardCard({ icon, title, description, to }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 text-2xl">{icon}</div>
      <h3 className="mb-2 text-lg font-semibold text-slate-800">{title}</h3>
      <p className="mb-4 text-sm text-slate-600">{description}</p>
      <Link
        to={to}
        className="inline-flex items-center rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
      >
        Open
      </Link>
    </article>
  );
}

export default DashboardCard;
