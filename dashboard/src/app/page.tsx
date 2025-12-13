'use client';

import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [health, setHealth] = useState({ pods: 4, cpu: 23, memory: 45, restarts: 0 });
  const [incidents, setIncidents] = useState<any[]>([]);
  const [status, setStatus] = useState('healthy');
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/incidents/detect');
      if (res.ok) {
        const data = await res.json();
        setIncidents(data.incidents || []);
        setStatus(data.incidents?.length > 0 ? 'degraded' : 'healthy');
      }
    } catch (e) {
      console.log('Using mock data');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
    setTimeout(() => setRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">🛡️ InfraGuard</h1>
            <p className="text-zinc-500 text-sm">AI-Powered Incident Response</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={handleRefresh}
              className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm"
            >
              {refreshing ? '⏳' : '🔄'} Refresh
            </button>
            <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm">
              ▶️ Run Analysis
            </button>
          </div>
        </div>

        {/* Status Banner */}
        <div className={`p-4 rounded-xl ${status === 'healthy' ? 'bg-emerald-500/20 border border-emerald-500/30' : 'bg-amber-500/20 border border-amber-500/30'}`}>
          <span className={`font-medium ${status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}`}>
            {status === 'healthy' ? '✅ All Systems Operational' : '⚠️ Issues Detected'}
          </span>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <p className="text-zinc-500 text-sm mb-1">Pods</p>
            <p className="text-2xl font-bold">{health.pods}/4</p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <p className="text-zinc-500 text-sm mb-1">CPU</p>
            <p className="text-2xl font-bold">{health.cpu}%</p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <p className="text-zinc-500 text-sm mb-1">Memory</p>
            <p className="text-2xl font-bold">{health.memory}%</p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <p className="text-zinc-500 text-sm mb-1">Restarts</p>
            <p className="text-2xl font-bold">{health.restarts}</p>
          </div>
        </div>

        {/* Two Columns */}
        <div className="grid grid-cols-2 gap-6">
          
          {/* Incidents */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <h2 className="font-semibold mb-4">🚨 Active Incidents</h2>
            {incidents.length === 0 ? (
              <p className="text-zinc-500 text-sm">No active incidents</p>
            ) : (
              <div className="space-y-2">
                {incidents.map((inc, i) => (
                  <div key={i} className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                    <p className="text-sm font-medium text-rose-400">{inc.type}</p>
                    <p className="text-xs text-zinc-400">{inc.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
            <h2 className="font-semibold mb-4">⚡ Recent Actions</h2>
            <p className="text-zinc-500 text-sm">No recent actions</p>
          </div>
        </div>

        {/* AI Summary */}
        <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-5">
          <h2 className="font-semibold mb-2">🤖 AI Agent Summary</h2>
          <p className="text-zinc-400 text-sm">
            {incidents.length === 0 
              ? 'All systems operational. Monitoring for anomalies...'
              : `Analyzing ${incidents.length} incident(s). Preparing remediation...`
            }
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-zinc-600 text-sm">
          Built with Cline • Kestra • Oumi • Vercel • CodeRabbit
        </p>

      </div>
    </div>
  );
}