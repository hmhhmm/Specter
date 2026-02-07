"use client";

import { motion } from "framer-motion";
import { Activity, Ghost } from "lucide-react";

export function MissionHeader() {
  return (
    <header className="relative w-full border-b border-white/5 bg-zinc-950/50 backdrop-blur-xl px-8 py-4 flex items-center justify-between z-20">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Ghost className="w-5 h-5 text-emerald-500" />
          <span className="font-bricolage text-lg font-bold tracking-tight text-white uppercase">
            Specter.AI
          </span>
        </div>
        
        <div className="h-4 w-px bg-white/10 hidden md:block" />
        
        <div className="flex items-center gap-3">
          <div className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </div>
          <h1 className="font-mono text-xs tracking-[0.2em] text-zinc-400 uppercase">
            Neural Link: Active Session
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-8">
        <div className="hidden lg:flex items-center gap-4">
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest leading-none mb-1">AI Core Status</span>
            <span className="text-[10px] font-mono text-emerald-500 uppercase tracking-widest leading-none">Optimal</span>
          </div>
          <div className="w-24 h-8 flex items-center justify-center opacity-50">
            <svg viewBox="0 0 100 40" className="w-full h-full stroke-emerald-500 fill-none stroke-2">
              <motion.path
                d="M0 20 L20 20 L25 10 L35 30 L40 20 L60 20 L65 5 L75 35 L80 20 L100 20"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ 
                  pathLength: [0, 1, 1],
                  opacity: [0, 1, 0.5],
                  x: [0, -10, 0]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
            </svg>
          </div>
        </div>

        <div className="px-3 py-1 rounded-md border border-white/10 bg-white/5 flex items-center gap-2">
          <Activity className="w-3 h-3 text-emerald-500" />
          <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-widest">Live</span>
        </div>
      </div>

      {/* Subtle Scanline Overlay for Header */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.05]">
        <motion.div 
          animate={{ x: ["-100%", "100%"] }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          className="h-full w-1/3 bg-gradient-to-r from-transparent via-emerald-500 to-transparent"
        />
      </div>
    </header>
  );
}
