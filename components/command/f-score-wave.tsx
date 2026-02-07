"use client";

import { motion } from "framer-motion";

export function FScoreWave() {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-end gap-3 mb-6">
        <span className="text-5xl font-bold font-bricolage text-red-500">8.2</span>
        <div className="flex flex-col mb-1.5">
          <span className="text-[9px] font-mono text-red-500 uppercase tracking-widest font-bold">Friction Index</span>
          <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-widest leading-none">Aggregated Score</span>
        </div>
      </div>
      
      <div className="flex-1 bg-zinc-950/40 rounded-2xl border border-white/5 p-4 overflow-hidden relative flex flex-col justify-between">
        <div className="absolute inset-0 opacity-10 pointer-events-none bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:10px_10px]" />
        
        <div className="relative h-24 w-full flex items-center">
          <svg viewBox="0 0 100 40" className="w-full h-full stroke-red-500/50 fill-none stroke-[1.5]">
            <motion.path
              d="M0 20 L5 5 L10 35 L15 10 L20 30 L25 5 L30 35 L35 15 L40 25 L45 5 L50 35 L55 10 L60 30 L65 5 L70 35 L75 15 L80 25 L85 5 L90 35 L95 10 L100 20"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
            <motion.path
              d="M0 20 L5 5 L10 35 L15 10 L20 30 L25 5 L30 35 L35 15 L40 25 L45 5 L50 35 L55 10 L60 30 L65 5 L70 35 L75 15 L80 25 L85 5 L90 35 L95 10 L100 20"
              initial={{ pathLength: 0, opacity: 0.5 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: 0.5 }}
              className="stroke-red-400 blur-sm"
            />
          </svg>
        </div>

        <p className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest leading-relaxed mt-4">
          Visualized <span className="text-red-400">Chaos Waveform</span>. High spikes indicate "Rage Clicks" and unhandled UI state locks.
        </p>
      </div>
    </div>
  );
}
