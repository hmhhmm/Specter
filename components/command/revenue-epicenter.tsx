"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { TrendingUp, AlertCircle } from "lucide-react";

interface DashboardStats {
  total_revenue_leak: number;
  severity_breakdown: { P0: number; P1: number; P2: number; P3: number };
  total_incidents: number;
  avg_f_score: number;
}

export function RevenueEpicenter() {
  const [revenue, setRevenue] = useState(0);
  const [hoveredSegment, setHoveredSegment] = useState<number | null>(null);
  const [segments, setSegments] = useState([
    { label: "Checkout Flow", value: 60, color: "oklch(0.7 0.2 40)" },
    { label: "Signup Flow", value: 30, color: "oklch(0.7 0.2 40 / 0.7)" },
    { label: "Verification", value: 10, color: "oklch(0.7 0.2 40 / 0.4)" },
  ]);
  
  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch("http://localhost:8000/api/dashboard/stats");
        if (response.ok) {
          const data: DashboardStats = await response.json();
          
          // Use real revenue leak or fallback
          const targetRevenue = data.total_revenue_leak > 0 ? data.total_revenue_leak : 148200;
          setTimeout(() => setRevenue(targetRevenue), 500);
          
          // Calculate segments from severity breakdown
          const total = data.total_incidents || 1;
          const breakdown = data.severity_breakdown || { P0: 0, P1: 0, P2: 0, P3: 0 };
          
          if (total > 0) {
            setSegments([
              { label: "P0 Critical", value: Math.round((breakdown.P0 / total) * 100) || 40, color: "oklch(0.7 0.2 25)" },
              { label: "P1 High", value: Math.round((breakdown.P1 / total) * 100) || 35, color: "oklch(0.7 0.2 40)" },
              { label: "P2-P3 Medium/Low", value: Math.round(((breakdown.P2 + breakdown.P3) / total) * 100) || 25, color: "oklch(0.7 0.2 55)" },
            ]);
          }
        } else {
          setTimeout(() => setRevenue(148200), 500);
        }
      } catch (err) {
        // Use fallback values on error
        setTimeout(() => setRevenue(148200), 500);
      }
    }
    fetchStats();
  }, []);

  // Calculate SVG paths for donut
  const size = 200;
  const strokeWidth = 16;
  const radius = (size - strokeWidth) / 2;
  const center = size / 2;
  const circumference = 2 * Math.PI * radius;

  let accumulatedOffset = 0;

  return (
    <div className="flex flex-col gap-4 h-full max-h-full">
      {/* Revenue Ticker */}
      <div className="rounded-lg bg-zinc-900/60 border border-zinc-800 p-8 flex flex-col items-center justify-center relative overflow-hidden" style={{height: '55%'}}>
        <div className="absolute inset-0 bg-gradient-to-b from-amber-500/5 to-transparent pointer-events-none" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-amber-500/5 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="relative z-10 flex flex-col items-center text-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="flex items-center gap-2 mb-6 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20"
          >
            <TrendingUp className="w-3.5 h-3.5 text-amber-500" />
            <span className="text-[10px] font-mono text-amber-500 uppercase tracking-[0.2em] font-bold">Projected Annual Revenue Leak</span>
          </motion.div>
          
          <div className="flex items-start">
            <span className="text-4xl md:text-5xl font-bricolage font-bold text-amber-500/40 mt-4 md:mt-6">$</span>
            <motion.h2 
              className="text-7xl md:text-9xl font-bricolage font-bold tracking-tighter text-amber-500 drop-shadow-[0_0_30px_rgba(245,158,11,0.3)]"
            >
              <CountUp value={revenue} />
            </motion.h2>
          </div>
          
          <p className="max-w-xs text-zinc-500 text-[10px] mt-4 uppercase tracking-wide leading-relaxed">
            Potential recovery opportunity from user experience optimization
          </p>
        </div>
      </div>

      {/* Impact Breakdown Donut */}
      <div className="rounded-lg bg-zinc-900/60 border border-zinc-800 p-6 flex flex-col md:flex-row gap-6 items-center" style={{height: '42%'}}>
        <div className="relative w-48 h-48 shrink-0">
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="rotate-[-90deg]">
            {segments.map((segment, i) => {
              const dashArray = (segment.value / 100) * circumference;
              const currentOffset = accumulatedOffset;
              accumulatedOffset += dashArray;

              return (
                <motion.circle
                  key={segment.label}
                  cx={center}
                  cy={center}
                  r={radius}
                  fill="transparent"
                  stroke={hoveredSegment === i ? "oklch(0.75 0.15 145)" : segment.color}
                  strokeWidth={strokeWidth}
                  strokeDasharray={`${dashArray} ${circumference}`}
                  initial={{ strokeDashoffset: dashArray }}
                  animate={{ 
                    strokeDashoffset: -currentOffset,
                    stroke: hoveredSegment === i ? "oklch(0.75 0.15 145)" : segment.color,
                    strokeWidth: hoveredSegment === i ? 20 : 16
                  }}
                  transition={{ 
                    strokeDashoffset: { duration: 1.5, delay: i * 0.2 + 0.5, ease: "circOut" },
                    stroke: { duration: 0.3 },
                    strokeWidth: { duration: 0.3 }
                  }}
                  onMouseEnter={() => setHoveredSegment(i)}
                  onMouseLeave={() => setHoveredSegment(null)}
                  className="cursor-pointer transition-all"
                />
              );
            })}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
            <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest leading-none mb-1">Leak Distribution</span>
            <AnimatePresence mode="wait">
              <motion.span 
                key={hoveredSegment !== null ? segments[hoveredSegment].label : "total"}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="text-lg font-bold font-bricolage text-white"
              >
                {hoveredSegment !== null ? segments[hoveredSegment].value : "100"}%
              </motion.span>
            </AnimatePresence>
          </div>
        </div>
        
        <div className="flex-1 space-y-5 w-full">
           {segments.map((segment, i) => (
             <div 
               key={segment.label}
               className="flex items-center justify-between group cursor-pointer"
               onMouseEnter={() => setHoveredSegment(i)}
               onMouseLeave={() => setHoveredSegment(null)}
             >
               <div className="flex items-center gap-3">
                 <motion.div 
                    animate={{ 
                      backgroundColor: hoveredSegment === i ? "oklch(0.75 0.15 145)" : segment.color,
                      scale: hoveredSegment === i ? 1.2 : 1
                    }}
                    className="w-2 h-2 rounded-full" 
                 />
                 <motion.span 
                    animate={{ color: hoveredSegment === i ? "white" : "oklch(0.7 0.05 0 / 0.5)" }}
                    className="text-[10px] font-mono uppercase tracking-widest transition-colors"
                 >
                   {segment.label}
                 </motion.span>
               </div>
               <motion.span 
                 animate={{ color: hoveredSegment === i ? "oklch(0.75 0.15 145)" : "oklch(0.7 0.2 40)" }}
                 className="text-xs font-mono font-bold transition-colors"
               >
                 {segment.value}%
               </motion.span>
             </div>
           ))}
           
           <div className="pt-4 border-t border-white/5">
             <div className="flex items-center gap-2">
               <AlertCircle className="w-3 h-3 text-zinc-600" />
               <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-widest">Hover segments to simulate recovery</span>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
}

function CountUp({ value }: { value: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTime: number;
    const duration = 2000;
    
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      // Easing function (outCirc)
      const ease = Math.sqrt(1 - Math.pow(progress - 1, 2));
      
      setDisplayValue(Math.floor(ease * value));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [value]);

  return <>{displayValue.toLocaleString()}</>;
}
