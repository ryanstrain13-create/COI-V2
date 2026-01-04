
import React from 'react';

interface PerformanceTabProps {
  playerName: string;
}

const PerformanceTab: React.FC<PerformanceTabProps> = ({ playerName }) => {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="bg-[#121214] border border-white/5 rounded-2xl p-8">
        <h3 className="text-xl font-bold mb-6">Archetype Analysis: 'The Dynamic Engine'</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
             <p className="text-zinc-400 text-sm mb-6 leading-relaxed">
               {playerName} is currently classified within the top 2% of NBA players in the 'Primary Engine' archetype. Using K-Means clustering across 142 distinct performance variables, our model identifies significant efficiency gains in pick-and-roll ball handling and corner gravity.
             </p>
             <div className="space-y-6">
               {[
                 { label: 'Offensive Efficiency (PPP)', val: 1.14, percentile: '98th' },
                 { label: 'Defensive Impact (EPM)', val: +2.1, percentile: '84th' },
                 { label: 'Usage Rate Delta', val: -4.2, percentile: 'Optimal' },
                 { label: 'TS% Over Expectation', val: +8.4, percentile: '92nd' },
               ].map((stat, i) => (
                 <div key={i} className="flex items-center justify-between border-b border-white/5 pb-4">
                   <div>
                     <span className="text-xs text-zinc-500 block mb-1 uppercase tracking-wider">{stat.label}</span>
                     <span className="text-xl font-bold">{stat.val}</span>
                   </div>
                   <div className="text-right">
                     <span className="text-[10px] text-zinc-500 block mb-1">PERCENTILE</span>
                     <span className="text-sm font-semibold text-blue-400">{stat.percentile}</span>
                   </div>
                 </div>
               ))}
             </div>
          </div>
          <div className="relative group">
            <div className="aspect-square bg-zinc-900 rounded-3xl border border-white/5 flex items-center justify-center p-8 overflow-hidden">
               {/* Visual placeholder for a complex clustering map or radar */}
               <div className="w-full h-full relative">
                 <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-48 h-48 bg-blue-500/20 rounded-full blur-3xl group-hover:bg-blue-500/40 transition-all"></div>
                 </div>
                 <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-blue-500 rounded-full"></div>
                 <div className="absolute top-1/2 left-1/3 w-3 h-3 bg-zinc-600 rounded-full opacity-50"></div>
                 <div className="absolute bottom-1/4 right-1/4 w-3 h-3 bg-zinc-600 rounded-full opacity-50"></div>
                 <div className="absolute top-1/2 right-1/3 w-3 h-3 bg-zinc-600 rounded-full opacity-50"></div>
                 <div className="absolute inset-0 border border-white/10 rounded-full"></div>
                 <div className="absolute inset-8 border border-white/5 rounded-full"></div>
                 <div className="absolute inset-24 border border-white/5 rounded-full"></div>
                 <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <p className="text-[10px] uppercase text-zinc-500 font-bold tracking-widest mb-1">Cluster</p>
                      <h4 className="text-3xl font-bold text-white tracking-tighter">Engine</h4>
                    </div>
                 </div>
               </div>
            </div>
            <p className="text-[10px] text-center text-zinc-500 mt-4 italic">K-Means spatial representation of player similarity vs league average</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-[#121214] border border-white/5 rounded-2xl p-8">
          <h3 className="text-lg font-semibold mb-4">Regression Forecasts</h3>
          <p className="text-sm text-zinc-500 mb-6">Bayesian modeling predicts a 4.2 season peak plateau based on current physical load data.</p>
          <div className="h-48 flex items-end gap-2 px-4">
             {[40, 65, 85, 95, 90, 80, 60, 45].map((h, i) => (
               <div key={i} className="flex-1 bg-zinc-800 rounded-t-lg group relative cursor-pointer">
                 <div className="absolute bottom-0 w-full bg-blue-500/40 rounded-t-lg group-hover:bg-blue-500 transition-all" style={{ height: `${h}%` }}></div>
                 <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] text-zinc-600 group-hover:text-white transition-colors">{24 + i}yr</span>
               </div>
             ))}
          </div>
        </div>

        <div className="bg-[#121214] border border-white/5 rounded-2xl p-8">
          <h3 className="text-lg font-semibold mb-4">Injury Probability Vectors</h3>
          <div className="space-y-4">
             {[
               { label: 'Ankle Stability', status: 'Stable', color: 'text-green-500' },
               { label: 'Knee Load', status: 'Elevated (L)', color: 'text-yellow-500' },
               { label: 'Lumbar Strain', status: 'Minimal', color: 'text-green-500' },
               { label: 'Recovery Index', status: '94%', color: 'text-blue-400' },
             ].map((inj, i) => (
               <div key={i} className="flex items-center justify-between p-3 bg-zinc-900/50 rounded-lg border border-white/5">
                 <span className="text-sm font-medium">{inj.label}</span>
                 <span className={`text-xs font-bold ${inj.color}`}>{inj.status}</span>
               </div>
             ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceTab;
