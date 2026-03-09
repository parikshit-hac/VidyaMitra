import useAuth from "../../hooks/useAuth";

function Navbar({ onMenu }) {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur md:px-6">
      <button
        onClick={onMenu}
        className="rounded-md border border-slate-200 px-3 py-1 text-sm text-slate-700 md:hidden"
      >
        Menu
      </button>
      <div className="hidden md:block">
        <h1 className="text-lg font-semibold text-slate-800">Dashboard</h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <p className="text-sm font-medium text-slate-800">{user?.full_name || "User"}</p>
          <p className="text-xs text-slate-500">{user?.email || ""}</p>
        </div>
        <button onClick={logout} className="rounded-md bg-slate-900 px-3 py-2 text-xs font-medium text-white hover:bg-slate-700">
          Logout
        </button>
      </div>
    </header>
  );
}

export default Navbar;
