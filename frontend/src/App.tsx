import React, { useState } from 'react';
import { Navigation, ActiveTab } from './components/Navigation.tsx';
import { GraphPage } from './pages/GraphPage.tsx';
import { MacroPage } from './pages/MacroPage.tsx';
import { MicroPage } from './pages/MicroPage.tsx';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('graph');

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1 flex flex-col">
        {activeTab === 'graph' && <GraphPage />}
        {activeTab === 'macro' && <MacroPage />}
        {activeTab === 'micro' && <MicroPage />}
      </main>
    </div>
  );
};

export default App;
