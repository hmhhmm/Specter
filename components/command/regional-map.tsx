"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function RegionalMap() {
  const [points, setPoints] = useState([
    { x: "25%", y: "35%", label: "US-West", issues: 0 },
    { x: "50%", y: "30%", label: "EU-West", issues: 0 },
    { x: "75%", y: "45%", label: "Asia-Pacific", issues: 0 },
  ]);

  useEffect(() => {
    async function fetchRegionalData() {
      try {
        const response = await fetch("http://localhost:8000/api/dashboard/stats");
        if (response.ok) {
          const data = await response.json();
          if (data.regional_data && data.regional_data.length > 0) {
            setPoints([
              { x: "25%", y: "35%", label: "NA", issues: data.regional_data[0]?.issues || 0 },
              { x: "50%", y: "30%", label: "EU", issues: data.regional_data[1]?.issues || 0 },
              { x: "75%", y: "45%", label: "APAC", issues: data.regional_data[2]?.issues || 0 },
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
    <div className="relative w-full h-full bg-zinc-950/40 rounded-2xl border border-white/5 overflow-hidden group">
      {/* Grid Pattern */}
      <div className="absolute inset-0 opacity-10 pointer-events-none bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:15px_15px]" />
      
      {/* Simplified Map Path */}
      <svg viewBox="0 0 200 100" className="w-full h-full opacity-20 stroke-zinc-700 fill-none stroke-[0.5]">
        <path d="M20 40 Q 30 30, 45 35 T 70 30 T 95 35 T 120 30 T 145 35 T 170 30 T 180 40" />
        <path d="M30 60 Q 50 50, 70 55 T 100 50 T 130 55 T 160 50 T 180 60" />
      </svg>

      {/* Pulse Markers */}
      {points.map((point, i) => (
        <div 
          key={point.label}
          className="absolute"
          style={{ left: point.x, top: point.y }}
        >
          <div className="relative">
            <motion.div 
              animate={{ scale: [1, 2], opacity: [0.5, 0] }}
              transition={{ duration: 2, repeat: Infinity, delay: i * 0.6 }}
              className={`absolute -inset-2 rounded-full ${point.issues > 0 ? 'bg-amber-500' : 'bg-emerald-500'}`}
            />
            <div className={`w-1.5 h-1.5 rounded-full ${point.issues > 0 ? 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]' : 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]'}`} />
            
            {/* Tooltip on Group Hover */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 px-2 py-1 bg-zinc-900 border border-white/10 rounded text-[8px] font-mono text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
              {point.label}: {point.issues > 0 ? `${point.issues} Issues` : 'Clear'}
            </div>
          </div>
        </div>
      ))}
      
      <div className="absolute bottom-3 left-4">
        <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-[0.2em]">Global Telemetry Active</span>
      </div>
    </div>
  );
}
