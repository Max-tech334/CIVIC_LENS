import { useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export default function InfluenceNetwork({ candidates, donors, donations }) {
  const graphData = useMemo(() => {
    const nodes = [];
    const links = [];

    // 1. Candidate Nodes (Blue Text)
    candidates.forEach(c => {
      nodes.push({ id: c.candidate_id, name: c.name, group: 'Candidate', color: '#2980b9' });
    });

    // 2. Donor Nodes (Green Text)
    donors.forEach(d => {
      nodes.push({ id: d.donor_id, name: d.name, group: 'Donor', color: '#27ae60' });
    });

    // 3. Links
    donations.forEach(d => {
      links.push({ source: d.donor_id, target: d.candidate_id, amount: d.amount });
    });

    return { nodes, links };
  }, [candidates, donors, donations]);

  if (!graphData.nodes.length) return <p style={{ padding: '20px' }}>No financial connections found for this selection.</p>;

  return (
    <div style={{ border: '1px solid #ccc', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#ffffff' }}>
      <ForceGraph2D
        graphData={graphData}
        width={960}
        height={500}
        linkColor={() => 'rgba(189, 195, 199, 0.6)'}
        linkWidth={link => Math.max(1, Math.sqrt(link.amount) / 40)} // Thicker lines for bigger donations
        
        // This is the magic that draws NAMES instead of dots!
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = node.group === 'Candidate' ? 16 / globalScale : 12 / globalScale;
          
          ctx.font = `${node.group === 'Candidate' ? 'bold' : 'normal'} ${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

          // Draw a soft white background box behind the text so lines don't block it
          ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

          // Draw the actual Text (Blue for Candidate, Green for Donor)
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = node.color;
          ctx.fillText(label, node.x, node.y);
          
          node.__bckgDimensions = bckgDimensions; // Save dimensions for hover effects
        }}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.fillStyle = color;
          const bckgDimensions = node.__bckgDimensions;
          bckgDimensions && ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);
        }}
      />
    </div>
  );
}