import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import L from 'leaflet'; 
import 'leaflet/dist/leaflet.css';

// Fix for default Leaflet icons in Vite/React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapVisualization = () => {
    const [geoData, setGeoData] = useState(null);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/geographic-influence')
            .then(res => {
                if (!res.ok) throw new Error("Backend not responding correctly");
                return res.json();
            })
            .then(data => {
                if (data && data.features) {
                    setGeoData(data);
                }
            })
            .catch(err => console.error("Map Engine Error:", err));
    }, []);

    // Light Theme Colors
    const getStyle = (feature) => {
        const fci = feature.properties.fci_score || 0;
        return {
            fillColor: fci > 15 ? '#b91c1c' : // High Concentration (Dark Red)
                       fci > 5  ? '#ef4444' : // Significant (Red)
                                  '#3b82f6',  // Minimal (Blue)
            weight: 1,
            opacity: 1,
            color: '#ffffff', // Clean white borders
            fillOpacity: 0.7,
        };
    };

    if (!geoData) return (
        <div className="flex items-center justify-center h-[600px] bg-slate-50 border border-slate-200 rounded-xl">
            <div className="text-slate-500 text-center p-20 animate-pulse font-sans">
                Loading Geospatial Data...
            </div>
        </div>
    );

    return (
        <div className="relative rounded-xl shadow-sm overflow-hidden border border-slate-200 bg-white">
            
            {/* Legend Overlay - Light Theme */}
            <div className="absolute bottom-6 left-6 z-[1000] bg-white/95 p-4 border border-slate-200 rounded-lg shadow-md text-xs text-slate-700 font-sans">
                <p className="font-bold text-blue-800 mb-2 uppercase tracking-tight">Funding Influence (FCI %)</p>
                <div className="space-y-2">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-[#b91c1c] rounded-sm"></div> 
                        <span>High Concentration (&gt;15%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-[#ef4444] rounded-sm"></div> 
                        <span>Significant (5-15%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-[#3b82f6] rounded-sm"></div> 
                        <span>Minimal ({"<"}5%)</span>
                    </div>
                </div>
            </div>

            {/* Explicit Height is Required */}
            <div style={{ height: '600px', width: '100%' }}>
                <MapContainer 
                    center={[0.0236, 37.9062]} 
                    zoom={6} 
                    style={{ height: '100%', width: '100%', background: '#f8fafc' }}
                    scrollWheelZoom={false}
                >
                    {/* Light Mode Carto Base */}
                    <TileLayer 
                        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; CARTO'
                    />
                    
                    <GeoJSON 
                        key={JSON.stringify(geoData.features[0]?.properties || 'empty')}
                        data={geoData} 
                        style={getStyle} 
                        onEachFeature={(feature, layer) => {
                            const name = feature.properties.COUNTY_NAM || feature.properties.COUNTY || "Unknown Territory";
                            const raised = feature.properties.total_raised || 0;
                            const score = feature.properties.fci_score || 0;

                            layer.bindPopup(`
                                <div style="color: #1e293b; font-family: system-ui, sans-serif; min-width: 150px;">
                                    <h4 style="margin:0; border-bottom: 2px solid #3b82f6; padding-bottom: 4px; font-weight: bold; text-transform: uppercase;">${name}</h4>
                                    <div style="margin-top: 8px;">
                                        <p style="margin: 4px 0;"><strong>Total Raised:</strong> KSh ${raised.toLocaleString()}</p>
                                        <p style="margin: 4px 0;"><strong>FCI Score:</strong> ${score}%</p>
                                    </div>
                                </div>
                            `);
                        }}
                    />
                </MapContainer>
            </div>
        </div>
    );
};

export default MapVisualization;