
import React, { useState } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

interface ContractAnalysisProps {
  playerName: string;
}

const scenarios = [
  { team: 'Lakers', salary: 45.2, fit: 94, market: 98, total: 143.4 },
  { team: 'Heat', salary: 38.5, fit: 88, market: 92, total: 130.5 },
  { team: 'Suns', salary: 42.1, fit: 82, market: 85, total: 126.3 },
  { team: 'Warriors', salary: 40.0, fit: 91, market: 95, total: 135.0 },
];

const radarData = [
  { subject: 'Financial Value', A: 95, fullMark: 100 },
  { subject: 'Team Fit', A: 85, fullMark: 100 },
  { subject: 'Market Growth', A: 92, fullMark: 100 },
  { subject: 'Winning Prob.', A: 78, fullMark: 100 },
  { subject: 'Longevity', A: 65, fullMark: 100 },
  { subject: 'Brand ROI', A: 98, fullMark: 100 },
];

const ContractAnalysis: React.FC<ContractAnalysisProps> = ({ playerName }) => {
  const [selectedScenario, setSelectedScenario] = useState(scenarios[0]);

  return (
    <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Strategic Decision Modeling</h2>
          <p className="text-zinc-500">Evaluating high-probability career paths for {playerName}</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          Run Simulation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-[#121214] border border-white/5 rounded-2xl p-8">
          <h3 className="text-lg font-semibold mb-6">Tradeoff Scenario Explorer</h3>
          <div className="space-y-4">
            {scenarios.map((s, i) => (
              <div 
                key={i} 
                onClick={() => setSelectedScenario(s)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedScenario.team === s.team 
                  ? 'bg-blue-600/10 border-blue-500/50 shadow-lg' 
                  : 'bg-zinc-900 border-white/5 hover:border-white/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center font-bold text-[10px] border border-white/5">
                      {s.team[0]}
                    </div>
                    <span className="font-medium">{s.team} Offer</span>
                  </div>
                  <span className="text-blue-400 font-bold">${s.salary}M/yr</span>
                </div>
                <div className="grid grid-cols-3 gap-4 mt-3">
                   <div className="text-[10px] uppercase text-zinc-500">
                     Fit Score <span className="block text-white text-xs mt-1">{s.fit}</span>
                   </div>
                   <div className="text-[10px] uppercase text-zinc-500">
                     Brand ROI <span className="block text-white text-xs mt-1">{s.market}</span>
                   </div>
                   <div className="text-[10px] uppercase text-zinc-500">
                     Total Value <span className="block text-white text-xs mt-1">${s.total}M</span>
                   </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#121214] border border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center">
          <h3 className="text-lg font-semibold mb-2 self-start">Comparative Archetype Fit</h3>
          <p className="text-zinc-500 text-sm mb-8 self-start">Selected Scenario: {selectedScenario.team}</p>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#ffffff10" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#71717a', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name={playerName}
                  dataKey="A"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.4}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-blue-900/10 border border-blue-500/20 rounded-2xl p-8">
        <div className="flex gap-6 items-start">
           <div className="w-12 h-12 bg-blue-500/20 text-blue-500 rounded-xl flex items-center justify-center text-2xl">💡</div>
           <div>
             <h3 className="text-lg font-semibold text-blue-400 mb-2">Coi Intelligence Insight</h3>
             <p className="text-zinc-300 text-sm leading-relaxed max-w-3xl">
               Our neural networks indicate that while the Suns offer a higher immediate base salary, the Lakers' scenario yields a 34% higher long-tail realized value due to tax efficiencies and regional endorsement density. Current prediction suggests that signing a 2+1 player option maximizes leverage for the 2027 salary cap spike.
             </p>
           </div>
        </div>
      </div>
    </div>
  );
};

export default ContractAnalysis;
