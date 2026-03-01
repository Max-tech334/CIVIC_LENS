// src/App.jsx
import { useState, useEffect } from 'react';
import { fetchCandidates } from './api';

function App() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      const data = await fetchCandidates();
      setCandidates(data);
      setLoading(false);
    };
    
    loadData();
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>🏛️ Civic Lens Laboratory</h1>
      <h2>Candidate Roster</h2>
      
      {loading ? (
        <p>Loading database...</p>
      ) : (
        <div style={{ display: 'grid', gap: '10px' }}>
          {candidates.map((candidate) => (
            <div 
              key={candidate.candidate_id} 
              style={{ border: '1px solid #ccc', padding: '10px', borderRadius: '5px' }}
            >
              <strong>{candidate.name}</strong> - {candidate.party} ({candidate.office_sought})
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;