import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { Tickets } from './pages/Tickets';
import { WorkflowDetail } from './pages/WorkflowDetail';
import { Approvals } from './pages/Approvals';
import { Agents } from './pages/Agents';
import { Logs } from './pages/Logs';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
        <Navbar />
        <div className="flex-1 flex overflow-hidden">
          <Sidebar />
          <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/tickets" element={<Tickets />} />
              <Route path="/tickets/:id" element={<WorkflowDetail />} />
              <Route path="/approvals" element={<Approvals />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/logs" element={<Logs />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
