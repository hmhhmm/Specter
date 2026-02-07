"use client";

import { motion } from "framer-motion";
import { ShieldAlert, TrendingDown, Database } from "lucide-react";

export function VaultHeader() {
  return (
    <div className="mb-12 relative">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="flex items-center gap-3 mb-6"
      >
        <div className="px-3 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-mono text-emerald-500 uppercase tracking-widest">
          Evidence Archive v4.2
        </div>
        <div className="h-px w-12 bg-zinc-800" />
        <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">
          Last Scan: 00:01:24 ago
        </div>
      </motion.div>

      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
        <div>
          <h1 className="text-5xl md:text-7xl font-bold font-bricolage tracking-tighter text-white mb-4 relative inline-block">
            <span className="relative z-10">Incident Repository</span>
            <motion.span 
              animate={{ 
                opacity: [0, 1, 0],
                x: [-2, 2, -2],
                clipPath: [
                  "inset(20% 0 50% 0)",
                  "inset(80% 0 10% 0)",
                  "inset(10% 0 80% 0)"
                ]
              }}
              transition={{ duration: 0.2, repeat: Infinity, repeatDelay: 3 }}
              className="absolute inset-0 z-0 text-emerald-500 opacity-50"
            >
              Incident Repository
            </motion.span>
          </h1>
          <p className="text-zinc-500 font-mono text-sm max-w-xl">
            Retrospective analysis of AI-detected friction points, visual regressions, and business impact vectors for <span className="text-emerald-500/80">novatrade.io</span>.
          </p>
        </div>

        <div className="flex gap-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="p-4 rounded-2xl bg-zinc-900/40 border border-white/5 backdrop-blur-sm flex items-center gap-4 min-w-[200px]"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <Database className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest mb-1">Active Cases</div>
              <div className="text-2xl font-bold font-bricolage text-white">07</div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="p-4 rounded-2xl bg-zinc-900/40 border border-red-500/10 backdrop-blur-sm flex items-center gap-4 min-w-[240px]"
          >
            <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-red-500 animate-pulse" />
            </div>
            <div>
              <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest mb-1">Revenue at Risk</div>
              <div className="text-2xl font-bold font-bricolage text-red-500">$50,500<span className="text-xs font-normal opacity-50 ml-1">/mo</span></div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
