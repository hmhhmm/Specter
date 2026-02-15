"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function FScoreWave() {
  const [avgFScore, setAvgFScore] = useState(0.74);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch("http://localhost:8000/api/dashboard/stats");
        if (response.ok) {
          const data = await response.json();
          if (data.avg_f_score > 0) {
            setAvgFScore(data.avg_f_score / 100);
          }
        }
      } catch (err) {
        console.error("Error fetching F-score:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-end gap-3 mb-6">
        <span className="text-5xl font-bold font-bricolage text-white">{loading ? "..." : avgFScore.toFixed(2)}</span>
        <div className="flex flex-col mb-1.5">
          <span className="text-[9px] font-mono text-emerald-500 uppercase tracking-widest font-bold">F-Score</span>
          <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-widest leading-none">Index Value</span>
        </div>
      </div>
      
      <div className="flex-1 bg-zinc-950/40 rounded-2xl border border-white/5 p-4 overflow-hidden relative flex flex-col justify-between">
        <div className="absolute inset-0 opacity-10 pointer-events-none bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:10px_10px]" />
        
        <div className="relative h-24 w-full flex items-center">
          <svg viewBox="0 0 100 40" className="w-full h-full stroke-emerald-500/50 fill-none stroke-[1.5]">
            <motion.path
              d="M0 20 L10 20 L15 5 L20 35 L25 20 L35 20 L40 5 L45 35 L50 20 L60 20 L65 10 L70 30 L75 20 L85 20 L90 5 L95 35 L100 20"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />
            <motion.path
              d="M0 20 L10 20 L15 5 L20 35 L25 20 L35 20 L40 5 L45 35 L50 20 L60 20 L65 10 L70 30 L75 20 L85 20 L90 5 L95 35 L100 20"
              initial={{ pathLength: 0, opacity: 0.5 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear", delay: 1 }}
              className="stroke-emerald-400 blur-sm"
            />
          </svg>
        </div>

        <p className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest leading-relaxed mt-4">
          Calculated based on <span className="text-zinc-300">Entropy Score</span> and <span className="text-zinc-300">Semantic Distance</span> of user interaction patterns.
        </p>
      </div>
    </div>
  );
}
