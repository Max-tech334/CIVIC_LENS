import { useState, useEffect } from 'react';
import { fetchCandidates, fetchDonations, fetchDonors } from './api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import InfluenceNetwork from './InfluenceNetwork';

function App() {
  const [candidates, setCandidates] = useState([]);
  const [donors, setDonors] = useState([]);
  const [donations, setDonations] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // NEW: State for the dropdown filter
  const [selectedCandidate, setSelectedCandidate] = useState('ALL');

  useEffect(() => {
    const loadData = async () => {
      const candidatesData = await fetchCandidates();
      const donationsData = await fetchDonations();
      const donorsData = await fetchDonors();

      // Chart Data Aggregation
      const financialTotals = {};
      donationsData.forEach((d) => {
        if (!financialTotals[d.candidate_id]) financialTotals[d.candidate_id] = 0;
        financialTotals[d.candidate_id] += d.amount;
      });

      const formattedChartData = candidatesData.map((c) => ({
        name: c.name,
        "Total Raised ($)": financialTotals[c.candidate_id] || 0,
      })).sort((a, b) => b["Total Raised ($)"] - a["Total Raised ($)"]);

      setCandidates(candidatesData);
      setDonors(donorsData);
      setDonations(donationsData);
      setChartData(formattedChartData);
      setLoading(false);
    };
    
    loadData();
  }, []);

  // --- FILTERING LOGIC ---
  // If 'ALL' is selected, show everything. Otherwise, only show the selected candidate's web.
  const filteredCandidates = selectedCandidate === 'ALL' 
    ? candidates 
    : candidates.filter(c => c.candidate_id === selectedCandidate);

  const filteredDonations = selectedCandidate === 'ALL'
    ? donations
    : donations.filter(d => d.candidate_id === selectedCandidate);

  // Only keep donors that actually gave money to the filtered candidates
  const connectedDonorIds = new Set(filteredDonations.map(d => d.donor_id));
  const filteredDonors = selectedCandidate === 'ALL'
    ? donors
    : donors.filter(d => connectedDonorIds.has(d.donor_id));

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', color: '#2c3e50' }}>🏛️ Civic Lens Laboratory</h1>
      
      {loading ? (
        <p style={{ textAlign: 'center' }}>Initializing Simulation Grid...</p>
      ) : (
        <>
          {/* THE NEW FILTERED INFLUENCE NETWORK */}
          <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '40px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h2 style={{ margin: 0, color: '#34495e' }}>Web of Influence</h2>
              
              {/* THE DROPDOWN MENU */}
              <select 
                value={selectedCandidate} 
                onChange={(e) => setSelectedCandidate(e.target.value)}
                style={{ padding: '10px', fontSize: '16px', borderRadius: '5px', border: '1px solid #ccc' }}
              >
                <option value="ALL">🌐 View All Candidates</option>
                {candidates.map(c => (
                  <option key={c.candidate_id} value={c.candidate_id}>
                    {c.name} ({c.party})
                  </option>
                ))}
              </select>
            </div>
            
            <p style={{ color: '#7f8c8d', fontSize: '14px', marginTop: 0 }}>
              * You can drag the names with your mouse. Candidate names are bolded blue.
            </p>
            
            {/* We pass the FILTERED data down to the graph */}
            <InfluenceNetwork 
              candidates={filteredCandidates} 
              donors={filteredDonors} 
              donations={filteredDonations} 
            />
          </div>

          {/* THE BAR CHART */}
          <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '40px' }}>
            <h2 style={{ marginTop: 0, color: '#34495e' }}>Campaign War Chests (Total Funds Raised)</h2>
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip cursor={{ fill: '#eee' }} />
                  <Legend />
                  <Bar dataKey="Total Raised ($)" fill="#27ae60" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;