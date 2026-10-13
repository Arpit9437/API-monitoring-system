import { Route, Routes } from "react-router-dom";

import { Dashboard } from "./pages/Dashboard";
import { MonitorDetail } from "./pages/MonitorDetail";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/monitors/:id" element={<MonitorDetail />} />
    </Routes>
  );
}
