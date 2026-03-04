import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';

import MapVisualization from './components/MapVisualization';
import NetworkGraph from './components/NetworkGraph';
import FundingTrends from './components/FundingTrends';
import AIExplainer from './components/AIExplainer';
import DashboardHome from './components/DashboardHome';
import DataIntake from './components/DataIntake';
import LandingPage from './components/LandingPage';
import PolicySimulator from './components/PolicySimulator';

// Extract the Header into a component so we can use the location router hook
const TopHeader = ({ sandboxMode, clearSandbox }) => {
  const location = useLocation();
  const isLanding = location.pathname === '/';
  const isHub = location.pathname === '/hub';

  return (
    <header className="border-b border-slate-200 bg-white p-6 shadow-sm sticky top-0 z-[2000]">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div>
          <Link to="/">
            <h1 className="text-3xl font-bold text-slate-800 tracking-tight hover:text-blue-700 transition-colors">
              CIVIC LENS <span className="text-blue-600 font-light">LABORATORY</span>
            </h1>
          </Link>
          <p className="text-slate-500 text-xs uppercase tracking-widest mt-1 font-semibold">
            Advanced Financial Intelligence Suite
          </p>
        </div>
        <div className="flex items-center gap-4">
          {/* Show a Return button if we are inside a module */}
          {(!isLanding && !isHub) && (
            <Link to="/hub" className="text-sm font-bold text-blue-600 hover:text-blue-800 bg-blue-50 px-4 py-2 rounded-lg border border-blue-100 transition-colors">
              ← Return to Hub
            </Link>
          )}
          
          {/* Dynamic Sandbox Indicator */}
          {sandboxMode ? (
            <div className="flex items-center gap-2">
              <div className="px-4 py-2 border border-purple-200 rounded-full bg-purple-50 text-[10px] animate-pulse">
                <span className="text-purple-700 font-bold">SYSTEM STATUS:</span> <span className="text-purple-600">ISOLATED SANDBOX</span>
              </div>
              <button onClick={clearSandbox} className="px-3 py-2 bg-red-50 hover:bg-red-100 text-red-600 text-[10px] font-bold rounded-full border border-red-200 transition-colors shadow-sm">
                EXIT SANDBOX
              </button>
            </div>
          ) : (
            <div className="px-4 py-2 border border-blue-100 rounded-full bg-blue-50 text-[10px]">
              <span className="text-blue-700 font-bold">SYSTEM STATUS:</span> <span className="text-blue-600">GLOBAL DATABASE</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

function App() {
  const [selectedCandidate, setSelectedCandidate] = useState("all");
  const [globalCandidates, setGlobalCandidates] = useState([]);
  
  // THE NEW BRAIN: Short-Term Memory for the Isolated Sandbox
  const [sandboxData, setSandboxData] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/candidates')
      .then(res => res.json())
      .then(data => setGlobalCandidates(data))
      .catch(err => console.error("Error fetching candidates:", err));
  }, []);

  // SMART DROPDOWNS: Determines which candidates show in the dropdowns
  const candidates = React.useMemo(() => {
    if (sandboxData && sandboxData.donations) {
      // If we are in Sandbox mode, ONLY show candidates from the uploaded document
      const uniqueNames = [...new Set(sandboxData.donations.map(d => d.candidate_name))];
      return uniqueNames.map(name => ({
        candidate_id: name.toLowerCase().replace(/ /g, "_").substring(0, 50),
        name: name,
        full_name: name
      }));
    }
    // Otherwise, show everyone from PostgreSQL
    return globalCandidates;
  }, [sandboxData, globalCandidates]);

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100">
        
        {/* Pass Sandbox status up to the Header */}
        <TopHeader sandboxMode={!!sandboxData} clearSandbox={() => setSandboxData(null)} />

        <main className="max-w-7xl mx-auto p-8 space-y-16">
          <Routes>
            {/* The Grand Entrance Landing Page */}
            <Route path="/" element={<LandingPage />} />

            {/* The 5-Card Hub (Global Database Mode) */}
            <Route path="/hub" element={<DashboardHome />} />

            {/* Module 1:  */}
            <Route path="/module-1" element={
              <section className="space-y-6">
                <div className="border-l-4 border-blue-600 pl-4">
                  <h2 className="text-2xl font-bold text-slate-800">Module 1: Funding Trends</h2>
                  <p className="text-slate-500 text-sm italic">Top war chests calculated from network donation data.</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8">
                  {/* Passing sandboxData down */}
                  <FundingTrends sandboxData={sandboxData} />
                </div>
              </section>
            } />

            {/* Module 2:  layout and visual weights box */}
            <Route path="/module-2" element={
              <section className="space-y-6">
                <div className="border-l-4 border-blue-600 pl-4 flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-800">Module 2: Network Intelligence Engine</h2>
                    <p className="text-slate-500 text-sm italic">Filtering financial nodes and edge-weight relationships.</p>
                  </div>
                  
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Focus Candidate</label>
                    <select 
                      value={selectedCandidate}
                      onChange={(e) => setSelectedCandidate(e.target.value)}
                      className="bg-white border border-slate-200 rounded-lg px-4 py-2 text-sm shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    >
                      <option value="all">Display Full Network</option>
                      {candidates.map(c => (
                        <option key={c.candidate_id} value={c.candidate_id}>{c.full_name || c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="md:col-span-1 space-y-4">
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                      <h4 className="font-bold text-blue-800 text-xs uppercase mb-2">Visual Weights</h4>
                      <p className="text-[11px] text-blue-900 leading-relaxed">
                        <strong>Edge Thickness:</strong> Scaled logarithmically. Thicker lines represent high-value transfers.
                      </p>
                      <p className="text-[11px] text-blue-900 leading-relaxed mt-2">
                        <strong>Edge Color:</strong> Stronger relationships fade from gray to deep blue.
                      </p>
                    </div>
                  </div>

                  <div className="md:col-span-3 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden relative">
                    {/* Passing sandboxData down */}
                    <NetworkGraph targetCandidateId={selectedCandidate} sandboxData={sandboxData} />
                  </div>
                </div>
              </section>
            } />

            {/* Module 3:  */}
            <Route path="/module-3" element={
              <section className="space-y-6">
                <div className="border-l-4 border-blue-600 pl-4">
                  <h2 className="text-2xl font-bold text-slate-800">Module 3: Geographic Influence Engine</h2>
                </div>
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                  {/* Passing sandboxData down */}
                  <MapVisualization sandboxData={sandboxData} />
                </div>
              </section>
            } />

            {/* Module 4: Policy Simulator */}
            <Route path="/module-4" element={
              <section className="space-y-6">
                <div className="border-l-4 border-rose-600 pl-4">
                  <h2 className="text-2xl font-bold text-slate-800">Module 4: Policy Simulator</h2>
                  <p className="text-slate-500 text-sm italic">Test hypothetical regulations and observe their impact on the power map.</p>
                </div>
                <PolicySimulator />
              </section>
            } />

            {/* Module 5: Candidate Dropdown so the AI knows who to analyze! */}
            <Route path="/module-5" element={
              <section className="space-y-6">
                <div className="border-l-4 border-blue-600 pl-4 flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-800">Module 5: AI Explainer Bot</h2>
                    <p className="text-slate-500 text-sm italic">Translating network complexity into accessible public summaries.</p>
                  </div>
                  
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Focus Candidate</label>
                    <select 
                      value={selectedCandidate}
                      onChange={(e) => setSelectedCandidate(e.target.value)}
                      className="bg-white border border-slate-200 rounded-lg px-4 py-2 text-sm shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    >
                      <option value="all">Select a candidate...</option>
                      {candidates.map(c => (
                        <option key={c.candidate_id} value={c.candidate_id}>{c.full_name || c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden p-6">
                  {/* Passing sandboxData down */}
                  <AIExplainer selectedCandidate={selectedCandidate} candidates={candidates} sandboxData={sandboxData} />
                </div>
              </section>
            } />

            {/* New Module: Data Intake Pipeline */}
            <Route path="/data-intake" element={
              <div className="bg-slate-50 border border-slate-200 rounded-xl shadow-sm p-2">
                {/* Giving DataIntake the ability to save to the sandbox! */}
                <DataIntake setSandboxData={setSandboxData} />
              </div>
            } />

          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;