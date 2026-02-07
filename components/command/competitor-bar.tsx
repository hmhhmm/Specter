"use client";

import { motion } from "framer-motion";

export function CompetitorBar() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="flex justify-between items-end">
          <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Specter Site</span>
          <span className="text-sm font-bold font-mono text-amber-500">1.4s</span>
        </div>
        <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: "70%" }}
            transition={{ duration: 1, delay: 0.5, ease: "circOut" }}
            className="h-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.3)]"
          />
        </div>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between items-end">
          <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Average Competitor</span>
          <span className="text-sm font-bold font-mono text-emerald-500">1.2s</span>
        </div>
        <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: "60%" }}
            transition={{ duration: 1, delay: 0.7, ease: "circOut" }}
            className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
          />
        </div>
      </div>
      <div className="pt-2 flex items-center gap-2">
        <div className="px-1.5 py-0.5 rounded bg-red-500/10 border border-red-500/20 text-[8px] font-mono text-red-500 uppercase tracking-widest font-bold">
          12% Performance Gap
        </div>
        <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest leading-none">Critical conversion risk detected</span>
      </div>
    </div>
  );
}
