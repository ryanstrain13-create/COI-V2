
import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, RadarChart, PolarGrid, PolarAngleAxis, Radar } from 'recharts';

interface ComparisonTabProps {
  playerName: string;
}

const playersList = ['LeBron James', 'Kevin Durant', 'Stephen Curry', 'Luka Doncic', 'Shai Gilgeous-Alexander', 'Giannis Antetokounmpo'];

const comparisonData = [
  { metric: 'Points', playerA: 28.4, playerB: 33.9 },
  { metric: 'Rebounds', playerA: 8.1, playerB: 9.2 },
  { metric: 'Assists', playerA: 7.4, playerB: 9.8 },
  { metric: 'FG%', playerA: 54.0, playerB: 48.7 },
  { metric: '3P%', playerA: 41.0, playerB: 37.5 },
];

const radarData = [
  { subject: 'Scoring', A: 92, B: 98, fullMark: 100 },
  { subject: 'Playmaking', A: 88, B: 95, fullMark: 100 },
  { subject: 'Defense', A: 75, B: 65, fullMark: 100 },
  { subject: 'Rebounding', A: 82, B: 89, fullMark: 100 },
  { subject: 'Gravity', A: 95, B: 90, fullMark: 100 },
];

const ComparisonTab: React.FC<ComparisonTabProps> = ({ playerName }) => {
  const [compPlayer, setCompPlayer] = useState('Luka Doncic');

  return (
    <div className="space-y-8 animate-in slide-in-from-right-4 duration-500">
      <div className="flex items-center justify-between bg-[#121214] p-6 rounded-2xl border border-white/5">
        <div>
          <h3 className="text-xl font-bold">Comparative Analysis</h3>
          <p className="text-zinc-500 text-sm">Direct performance benchmark vs league peers</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <span className="text-[10px] text-zinc-500 font-bold uppercase block">Benchmark Target</span>
            <select 
              value={compPlayer}
              onChange={(e) => setCompPlayer(e.target.value)}
              className="bg-zinc-800 border border-white/5 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
            >
              {playersList.filter(p => p !== playerName).map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-[#121214] border border-white/5 rounded-2xl p-8">
          <h4 className="text-lg font-semibold mb-8 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500"></span> Statistical Delta
          </h4>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} layout="vertical" barGap={8}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#ffffff08" />
                <XAxis type="number" hide />
                <YAxis dataKey="metric" type="category" stroke="#71717a" fontSize={12} width={80} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{ fill: '#ffffff05' }}
                  contentStyle={{ backgroundColor: '#18181b', border: 'none', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)' }}
                />
                <Legend iconType="circle" />
                <Bar name={playerName} dataKey="playerA" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                <Bar name={compPlayer} dataKey="playerB" fill="#a855f7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#121214] border border-white/5 rounded-2xl p-8">
           <h4 className="text-lg font-semibold mb-8 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-purple-500"></span> Archetype Overlap
          </h4>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#ffffff10" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#71717a', fontSize: 10 }} />
                <Radar name={playerName} dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.5} />
                <Radar name={compPlayer} dataKey="B" stroke="#a855f7" fill="#a855f7" fillOpacity={0.5} />
                <Tooltip 
                   contentStyle={{ backgroundColor: '#18181b', border: 'none', borderRadius: '12px' }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Marketability Variance', value: '+14.2%', desc: `Endorsement potential vs ${compPlayer.split(' ')[0]}`, icon: '📈' },
          { label: 'Winning Impact', value: 'High', desc: 'Net rating similarity is within 1.2pts', icon: '🏆' },
          { label: 'Longevity Comp', value: '92%', desc: 'Health trajectory matches peak profiles', icon: '⏳' },
        ].map((item, i) => (
          <div key={i} className="bg-zinc-900/40 border border-white/5 p-6 rounded-2xl hover:bg-zinc-900/60 transition-colors group">
            <div className="text-2xl mb-3 group-hover:scale-110 transition-transform inline-block">{item.icon}</div>
            <p className="text-xs text-zinc-500 font-bold uppercase tracking-widest mb-1">{item.label}</p>
            <h5 className="text-2xl font-bold mb-2">{item.value}</h5>
            <p className="text-xs text-zinc-400 leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComparisonTab;
