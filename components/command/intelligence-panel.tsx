"use client";

import { Map, Zap, GitBranch } from "lucide-react";
import { RegionalMap } from "./regional-map";
import { CompetitorBar } from "./competitor-bar";
import { RootCausePanel } from "./root-cause-panel";

export function IntelligencePanel() {
  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Regional Map */}
      <div className="rounded-lg bg-zinc-900/60 border border-zinc-800 p-4 flex flex-col h-[160px]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Map className="w-4 h-4 text-blue-400" />
            <h3 className="text-[10px] font-medium text-zinc-400 uppercase tracking-wide">Regional Analysis</h3>
          </div>
          <div className="px-2 py-0.5 rounded border border-blue-500/20 bg-blue-500/10 text-[8px] font-medium text-blue-400 uppercase tracking-wide">
            Active
          </div>
        </div>
        <div className="flex-1">
          <RegionalMap />
        </div>
      </div>

      {/* Competitor Benchmarking */}
      <div className="rounded-lg bg-zinc-900/60 border border-zinc-800 p-3 flex flex-col">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-blue-400" />
          <h3 className="text-[10px] font-medium text-zinc-400 uppercase tracking-wide">Competitive Analysis</h3>
        </div>
        <CompetitorBar />
      </div>

      {/* Root Cause Intelligence */}
      <div className="rounded-lg bg-zinc-900/60 border border-zinc-800 p-3 flex flex-col">
        <div className="flex items-center gap-2 mb-3">
          <GitBranch className="w-4 h-4 text-blue-400" />
          <h3 className="text-[10px] font-medium text-zinc-400 uppercase tracking-wide">Recurring Patterns</h3>
        </div>
        <RootCausePanel />
      </div>
    </div>
  );
}
