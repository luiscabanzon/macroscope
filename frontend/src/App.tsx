import React, { useState } from 'react';
import { Navigation, ActiveTab } from './components/Navigation.tsx';
import { GraphPage } from './pages/GraphPage.tsx';
import { MacroPage } from './pages/MacroPage.tsx';
import { MicroPage } from './pages/MicroPage.tsx';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('graph');
  const [selectedCompanyForMicro, setSelectedCompanyForMicro] = useState<string>('NVDA');

  const handleDeepDive = (ticker: string) => {
    setSelectedCompanyForMicro(ticker);
    setActiveTab('micro');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1 flex flex-col">
        {activeTab === 'graph' && <GraphPage onDeepDive={handleDeepDive} />}
        {activeTab === 'macro' && <MacroPage />}
        {activeTab === 'micro' && <MicroPage initialTicker={selectedCompanyForMicro} />}
      </main>
    </div>
  );
};

export default App;
