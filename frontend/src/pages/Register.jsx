import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import useAuth from "../hooks/useAuth";

function Register() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await register(form.full_name, form.email, form.password);
      navigate("/");
    } catch (err) {
      setError(err?.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="mb-1 text-2xl font-bold text-slate-900">Register</h1>
        <p className="mb-5 text-sm text-slate-500">Create your VidyaMitra account.</p>
        {error && <p className="mb-3 rounded-md bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        <div className="space-y-3">
          <input
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Full name"
            value={form.full_name}
            onChange={(e) => setForm((s) => ({ ...s, full_name: e.target.value }))}
            required
          />
          <input
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm((s) => ({ ...s, email: e.target.value }))}
            required
          />
          <input
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm((s) => ({ ...s, password: e.target.value }))}
            required
          />
        </div>
        <button disabled={loading} className="mt-4 w-full rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white">
          {loading ? "Please wait..." : "Register"}
        </button>
        <p className="mt-4 text-sm text-slate-600">
          Already have account? <Link to="/login" className="text-brand-700">Login</Link>
        </p>
      </form>
    </div>
  );
}

export default Register;
