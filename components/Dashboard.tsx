
import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DashboardProps {
  playerName: string;
}

const data = [
  { name: '2019', value: 35, ppg: 25.3 },
  { name: '2020', value: 42, ppg: 27.1 },
  { name: '2021', value: 38, ppg: 26.8 },
  { name: '2022', value: 48, ppg: 28.5 },
  { name: '2023', value: 52, ppg: 29.7 },
  { name: '2024', value: 60, ppg: 31.4 },
];

const Dashboard: React.FC<DashboardProps> = ({ playerName }) => {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-top-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Welcome back, {playerName.split(' ')[0]}</h2>
          <p className="text-zinc-500">Your career trajectory is currently <span className="text-green-500 font-semibold font-mono">OPTIMAL</span></p>
        </div>
        <div className="flex gap-2">
           <button className="bg-zinc-800 hover:bg-zinc-700 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-lg transition-colors border border-white/5">Customize View</button>
           <button className="bg-blue-600 hover:bg-blue-500 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-lg transition-colors shadow-lg shadow-blue-500/20">Sync NBA Data</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          { label: 'Current Valuation', value: '$52.4M', change: '+12%', color: 'text-blue-500', icon: '💰' },
          { label: 'Global Rank', value: '#4', change: 'Top 1%', color: 'text-emerald-500', icon: '🌎' },
          { label: 'Brand Power', value: '92.1', change: 'Elite', color: 'text-purple-500', icon: '⚡' },
          { label: 'Usage Optimization', value: '31.4%', change: '-2.1%', color: 'text-orange-500', icon: '⚙️' },
        ].map((stat, i) => (
          <div key={i} className="bg-[#121214] border border-white/5 rounded-2xl p-5 hover:border-white/20 transition-all group relative overflow-hidden">
            <div className="absolute top-2 right-2 text-xl opacity-20 group-hover:opacity-100 transition-opacity">{stat.icon}</div>
            <p className="text-zinc-500 text-[10px] font-bold uppercase tracking-widest mb-1">{stat.label}</p>
            <div className="flex items-end justify-between">
              <h3 className={`text-2xl font-bold ${stat.color}`}>{stat.value}</h3>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-white/5 text-zinc-400">{stat.change}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-[#121214] border border-white/5 rounded-2xl p-8 relative">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-lg font-semibold">Value Projection vs Performance Peaks</h3>
              <p className="text-xs text-zinc-500">Correlation between Salary (M) and PPG efficiency</p>
            </div>
            <div className="flex gap-4">
               <div className="flex items-center gap-1.5">
                 <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                 <span className="text-[10px] text-zinc-500 font-bold uppercase">Valuation</span>
               </div>
               <div className="flex items-center gap-1.5">
                 <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                 <span className="text-[10px] text-zinc-500 font-bold uppercase">Efficiency</span>
               </div>
            </div>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPpg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff08" />
                <XAxis dataKey="name" stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} dy={10} />
                <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}M`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid #ffffff10', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorVal)" />
                <Area type="monotone" dataKey="ppg" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorPpg)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#121214] border border-white/5 rounded-2xl p-8 flex flex-col h-full">
          <h3 className="text-lg font-semibold mb-2">Historical Peaks</h3>
          <p className="text-zinc-500 text-xs mb-6">Key milestones from your NBA career history.</p>
          <div className="flex-1 space-y-5 overflow-y-auto pr-2 custom-scrollbar">
            {[
              { year: '2023-24', event: 'NBA All-Star Starter', type: 'award' },
              { year: '2022-23', event: 'Scoring Title (31.4 PPG)', type: 'milestone' },
              { year: '2021-22', event: 'All-NBA First Team', type: 'award' },
              { year: '2020-21', event: 'Western Conference Finals', type: 'milestone' },
              { year: '2019-20', event: 'Contract Extension Signed', type: 'milestone' },
            ].map((m, i) => (
              <div key={i} className="flex gap-4 group">
                <div className="flex flex-col items-center">
                  <div className={`w-2 h-2 rounded-full mt-1.5 ${m.type === 'award' ? 'bg-amber-500' : 'bg-blue-500'}`}></div>
                  <div className="w-px flex-1 bg-white/5 mt-1"></div>
                </div>
                <div className="pb-4">
                  <span className="text-[10px] text-zinc-500 font-mono font-bold">{m.year}</span>
                  <h5 className="text-sm font-medium group-hover:text-blue-400 transition-colors">{m.event}</h5>
                </div>
              </div>
            ))}
          </div>
          <button className="w-full mt-6 py-3 bg-zinc-800 hover:bg-zinc-700 rounded-xl text-xs font-bold uppercase tracking-widest transition-all">
            Full Career Archive
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
