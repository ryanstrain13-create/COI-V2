
import React from 'react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Home', icon: '🏠' },
    { id: 'performance', label: 'Performance', icon: '📈' },
    { id: 'comparison', label: 'Comparison', icon: '⚖️' },
    { id: 'contracts', label: 'Decision Hub', icon: '💼' },
  ];

  return (
    <aside className="w-64 border-r border-white/10 flex flex-col h-full bg-[#0d0d0e] z-30">
      <div className="p-8">
        <h1 className="text-3xl font-black text-white tracking-tighter italic">COI<span className="text-blue-500">.</span></h1>
        <p className="text-[9px] uppercase tracking-[0.2em] text-zinc-500 font-bold mt-2">Intelligence Studio</p>
      </div>
      
      <nav className="flex-1 px-4 py-4">
        <ul className="space-y-1.5">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 group ${
                  activeTab === item.id 
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/10' 
                  : 'text-zinc-500 hover:text-white hover:bg-zinc-800/50'
                }`}
              >
                <span className={`text-lg transition-transform group-hover:scale-110 ${activeTab === item.id ? 'grayscale-0' : 'grayscale opacity-70 group-hover:grayscale-0 group-hover:opacity-100'}`}>
                  {item.icon}
                </span>
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-6 mt-auto">
        <div className="bg-zinc-900/50 p-5 rounded-2xl border border-white/5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-2 opacity-10">
            <span className="text-4xl">📊</span>
          </div>
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold mb-3">Live Marketability</p>
          <div className="flex items-center justify-between mb-2">
            <span className="text-lg font-bold">88.4</span>
            <span className="text-[10px] text-green-500 font-mono bg-green-500/10 px-1.5 py-0.5 rounded">+1.2%</span>
          </div>
          <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
             <div className="h-full bg-blue-500 w-4/5 rounded-full"></div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
