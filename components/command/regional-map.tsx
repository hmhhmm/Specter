"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function RegionalMap() {
  const [regions, setRegions] = useState([
    { id: "na", name: "North America", x: 20, y: 30, issues: 0, status: "healthy" },
    { id: "eu", name: "Europe", x: 50, y: 25, issues: 0, status: "healthy" },
    { id: "apac", name: "Asia Pacific", x: 75, y: 35, issues: 0, status: "healthy" },
    { id: "sa", name: "South America", x: 30, y: 65, issues: 0, status: "healthy" },
  ]);

  useEffect(() => {
    async function fetchRegionalData() {
      try {
        const response = await fetch("http://localhost:8000/api/dashboard/stats");
        if (response.ok) {
          const data = await response.json();
          if (data.regional_data && data.regional_data.length > 0) {
            setRegions([
              { id: "na", name: "North America", x: 20, y: 30, issues: data.regional_data[0]?.issues || 0, status: (data.regional_data[0]?.issues || 0) > 0 ? "warning" : "healthy" },
              { id: "eu", name: "Europe", x: 50, y: 25, issues: data.regional_data[1]?.issues || 0, status: (data.regional_data[1]?.issues || 0) > 0 ? "warning" : "healthy" },
              { id: "apac", name: "Asia Pacific", x: 75, y: 35, issues: data.regional_data[2]?.issues || 0, status: (data.regional_data[2]?.issues || 0) > 0 ? "warning" : "healthy" },
              { id: "sa", name: "South America", x: 30, y: 65, issues: 0, status: "healthy" },
            ]);
          }
        }
      } catch (err) {
        console.error("Error fetching regional data:", err);
      }
    }
    fetchRegionalData();
  }, []);

  return (
    <div className="relative w-full h-full bg-zinc-950/60 rounded-lg border border-zinc-800/50 overflow-hidden">
      {/* World Map Background */}
      <svg viewBox="0 0 100 80" className="w-full h-full opacity-10 absolute inset-0">
        <defs>
          <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-zinc-700"/>
          </pattern>
        </defs>
        <rect width="100" height="80" fill="url(#grid)" />
      </svg>

      {/* Region Cards */}
      <div className="relative w-full h-full">
        {regions.map((region, i) => (
          <div 
            key={region.id}
            className="absolute transition-transform hover:scale-110"
            style={{ left: `${region.x}%`, top: `${region.y}%`, transform: 'translate(-50%, -50%)' }}
          >
            <div className="flex flex-col items-center gap-1">
              {/* Status Indicator */}
              <div className={`w-2 h-2 rounded-full ${region.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'} shadow-lg`}>
                <div className={`w-2 h-2 rounded-full ${region.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'} animate-ping opacity-75`} />
              </div>
              
              {/* Region Label */}
              <div className="px-2 py-0.5 rounded bg-zinc-900/80 border border-zinc-700/50 backdrop-blur-sm">
                <div className="text-[7px] font-medium text-zinc-400 whitespace-nowrap">{region.name}</div>
                {region.issues > 0 && (
                  <div className="text-[6px] text-amber-400 text-center">{region.issues} issues</div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
