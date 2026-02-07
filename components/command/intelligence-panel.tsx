"use client";

import { Map, Zap, Activity } from "lucide-react";
import { RegionalMap } from "./regional-map";
import { CompetitorBar } from "./competitor-bar";
import { FScoreWave } from "./f-score-wave";

export function IntelligencePanel() {
  return (
    <div className="flex flex-col gap-6 h-full">
      {/* Regional Map */}
      <div className="rounded-[2.5rem] bg-zinc-900/40 border border-white/5 p-6 flex flex-col h-[300px] shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Map className="w-4 h-4 text-emerald-500" />
            <h3 className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest font-bold">Regional Leak Map</h3>
          </div>
          <div className="px-2 py-0.5 rounded border border-emerald-500/20 bg-emerald-500/5 text-[8px] font-mono text-emerald-500 uppercase tracking-widest animate-pulse">
            Active
          </div>
        </div>
        <div className="flex-1">
          <RegionalMap />
        </div>
      </div>

      {/* Competitor Benchmarking */}
      <div className="rounded-[2.5rem] bg-zinc-900/40 border border-white/5 p-6 flex flex-col shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <Zap className="w-4 h-4 text-amber-500" />
          <h3 className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest font-bold">Anxiety Indices (vs Industry)</h3>
        </div>
        <CompetitorBar />
      </div>

      {/* Friction Index Waveform */}
      <div className="rounded-[2.5rem] bg-zinc-900/40 border border-white/5 p-6 flex flex-col flex-1 shadow-sm overflow-hidden">
        <div className="flex items-center gap-2 mb-6">
          <Activity className="w-4 h-4 text-red-500" />
          <h3 className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest font-bold">Friction Index</h3>
        </div>
        <FScoreWave />
      </div>
    </div>
  );
}
