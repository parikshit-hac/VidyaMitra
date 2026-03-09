import { useState } from "react";

import Footer from "./Footer";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function AppLayout({ children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="md:ml-64">
        <Navbar onMenu={() => setOpen(true)} />
        <main className="p-4 md:p-6">{children}</main>
        <Footer />
      </div>
    </div>
  );
}

export default AppLayout;
