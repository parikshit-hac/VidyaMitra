import { Link } from "react-router-dom";

function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-center">
        <h1 className="text-2xl font-bold text-slate-900">Page Not Found</h1>
        <p className="mt-2 text-sm text-slate-600">The route you requested does not exist.</p>
        <Link to="/" className="mt-4 inline-block rounded-md bg-brand-600 px-3 py-2 text-sm text-white">Go Dashboard</Link>
      </div>
    </div>
  );
}

export default NotFound;
