import React, { useEffect, useState } from 'react';
import { Ticket } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Plus, Play, Sparkles, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Tickets: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [search, setSearch] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [customerId, setCustomerId] = useState<string>('CUST-9901');
  const [submitting, setSubmitting] = useState<boolean>(false);

  const navigate = useNavigate();

  useEffect(() => {
    loadTickets();
  }, []);

  async function loadTickets() {
    try {
      const data = await api.getTickets();
      setTickets(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleCreateTicket(e: React.FormEvent) {
    e.preventDefault();
    if (!title || !description) return;
    setSubmitting(true);
    try {
      const newTicket = await api.createTicket({ title, description, customer_id: customerId });
      // Trigger workflow automatically
      const wfRes = await api.runWorkflow(newTicket.id);
      setIsModalOpen(false);
      setTitle('');
      setDescription('');
      await loadTickets();
      navigate(`/tickets/${newTicket.id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRunWorkflow(ticketId: string) {
    try {
      await api.runWorkflow(ticketId);
      await loadTickets();
      navigate(`/tickets/${ticketId}`);
    } catch (err) {
      console.error(err);
    }
  }

  const filteredTickets = tickets.filter(
    t => t.title.toLowerCase().includes(search.toLowerCase()) ||
         t.id.toLowerCase().includes(search.toLowerCase()) ||
         (t.category && t.category.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Support Tickets</h2>
          <p className="text-xs text-slate-400">Submit and inspect multi-agent automated tickets</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-sky-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Support Ticket</span>
        </button>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
        <input
          type="text"
          placeholder="Filter tickets by ID, title, or category..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-800/80 border border-slate-700/60 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
        />
      </div>

      {/* Tickets Table */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400 border-b border-slate-700/50">
            <tr>
              <th className="py-3.5 px-4">Ticket ID</th>
              <th className="py-3.5 px-4">Title</th>
              <th className="py-3.5 px-4">Category</th>
              <th className="py-3.5 px-4">Priority</th>
              <th className="py-3.5 px-4">Department</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredTickets.map((t) => (
              <tr key={t.id} className="hover:bg-slate-800/40">
                <td className="py-3.5 px-4 font-mono text-xs text-sky-400 font-semibold">{t.id}</td>
                <td className="py-3.5 px-4 font-medium text-slate-200">{t.title}</td>
                <td className="py-3.5 px-4 text-xs text-slate-400">{t.category || 'Unclassified'}</td>
                <td className="py-3.5 px-4 text-xs text-slate-400">{t.priority || 'Medium'}</td>
                <td className="py-3.5 px-4 text-xs text-slate-400">{t.assigned_team || 'Unassigned'}</td>
                <td className="py-3.5 px-4"><StatusBadge status={t.status} /></td>
                <td className="py-3.5 px-4 text-right space-x-2">
                  <button
                    onClick={() => handleRunWorkflow(t.id)}
                    className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 bg-sky-500/10 text-sky-400 border border-sky-500/30 hover:bg-sky-500/20 rounded-lg font-medium transition"
                  >
                    <Play className="w-3 h-3" />
                    <span>Run Graph</span>
                  </button>
                  <button
                    onClick={() => navigate(`/tickets/${t.id}`)}
                    className="text-xs px-2.5 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-slate-200 font-medium transition"
                  >
                    Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal Create Ticket */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-lg space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Create & Run Ticket Workflow</h3>
            <form onSubmit={handleCreateTicket} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Ticket Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Payment failed three times but money deducted"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Customer Message / Description</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Detailed customer message describing the support issue..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Customer ID</label>
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-xl text-xs font-medium text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-sky-500/20"
                >
                  {submitting ? 'Running Multi-Agent Workflow...' : 'Submit & Process'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
