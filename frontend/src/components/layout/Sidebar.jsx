import { Link, NavLink } from "react-router-dom";

const links = [
  { label: "Dashboard", to: "/" },
  { label: "Career Support", to: "/career-support" },
  { label: "Resume Analysis", to: "/resume-analysis" },
  { label: "Skills Evaluation", to: "/skills-evaluation" },
  { label: "Dynamic Quiz", to: "/dynamic-quiz" },
  { label: "Learning Resources", to: "/learning-resources" },
  { label: "Interview Simulator", to: "/interview-simulator" },
  { label: "Market Insights", to: "/market-insights" }
];

function Sidebar({ open, onClose }) {
  return (
    <>
      <div
        onClick={onClose}
        className={`fixed inset-0 z-20 bg-slate-900/45 transition md:hidden ${open ? "block" : "hidden"}`}
      />
      <aside
        className={`fixed left-0 top-0 z-30 h-full w-64 border-r border-slate-200 bg-white p-4 shadow-sm transition-transform md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="mb-8">
          <Link to="/" className="text-xl font-bold text-brand-600">
            VidyaMitra
          </Link>
          <p className="text-xs text-slate-500">AI Career Support Platform</p>
        </div>
        <nav className="space-y-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              onClick={onClose}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}

export default Sidebar;
