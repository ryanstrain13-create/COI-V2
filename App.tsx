
import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import ContractAnalysis from './components/ContractAnalysis';
import PerformanceTab from './components/PerformanceTab';
import ComparisonTab from './components/ComparisonTab';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedPlayer, setSelectedPlayer] = useState('LeBron James');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard playerName={selectedPlayer} />;
      case 'contracts':
        return <ContractAnalysis playerName={selectedPlayer} />;
      case 'performance':
        return <PerformanceTab playerName={selectedPlayer} />;
      case 'comparison':
        return <ComparisonTab playerName={selectedPlayer} />;
      default:
        return <Dashboard playerName={selectedPlayer} />;
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0a0b] text-white overflow-hidden font-sans">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 overflow-y-auto bg-[#0a0a0b] relative">
        <header className="h-16 border-b border-white/10 flex items-center justify-between px-8 sticky top-0 bg-[#0a0a0b]/80 backdrop-blur-md z-20">
          <div className="flex items-center gap-4">
             <h2 className="text-xl font-semibold capitalize tracking-tight">{activeTab.replace('-', ' ')}</h2>
             <div className="h-4 w-px bg-white/10 mx-2"></div>
             <span className="text-xs font-medium text-zinc-500 uppercase tracking-widest">Intelligence Studio Portal</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center bg-zinc-900 border border-white/5 rounded-full px-4 py-1.5 gap-3">
              <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-tighter">Active Profile:</span>
              <select 
                value={selectedPlayer}
                onChange={(e) => setSelectedPlayer(e.target.value)}
                className="bg-transparent text-sm font-semibold focus:outline-none cursor-pointer text-blue-400"
              >
                <option value="LeBron James">LeBron James</option>
                <option value="Kevin Durant">Kevin Durant</option>
                <option value="Stephen Curry">Stephen Curry</option>
                <option value="Luka Doncic">Luka Doncic</option>
                <option value="Shai Gilgeous-Alexander">Shai G.-Alexander</option>
              </select>
            </div>
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center font-bold text-xs shadow-lg shadow-blue-500/20">
              {selectedPlayer.split(' ').map(n => n[0]).join('')}
            </div>
          </div>
        </header>
        <div className="p-8 max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </main>
      
      {/* Persistent Floating AI Agent */}
      <ChatInterface playerName={selectedPlayer} />
    </div>
  );
};

export default App;
