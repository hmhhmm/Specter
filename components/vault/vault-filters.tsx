"use client";

import { motion } from "framer-motion";
import { ChevronDown, Filter } from "lucide-react";
import { cn } from "@/lib/utils";

interface VaultFiltersProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
}

export function VaultFilters({ activeFilter, onFilterChange }: VaultFiltersProps) {
  const filters = [
    { id: "all", label: "All Incidents", color: "zinc" },
    { id: "P0", label: "P0 Critical", color: "red" },
    { id: "P1", label: "P1 High", color: "amber" },
    { id: "P2", label: "P2 Medium", color: "yellow" },
    { id: "P3", label: "P3 Low", color: "blue" },
  ];

  const getColorClasses = (color: string, isActive: boolean) => {
    if (!isActive) return "bg-zinc-900/40 border-white/5 text-zinc-500 hover:border-white/10 hover:text-zinc-300";
    
    switch (color) {
      case "red": return "bg-red-500/10 border-red-500/30 text-red-400";
      case "amber": return "bg-amber-500/10 border-amber-500/30 text-amber-400";
      case "yellow": return "bg-yellow-500/10 border-yellow-500/30 text-yellow-400";
      case "blue": return "bg-blue-500/10 border-blue-500/30 text-blue-400";
      default: return "bg-emerald-500/10 border-emerald-500/30 text-emerald-400";
    }
  };

  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-6 mb-10 pb-6 border-b border-white/5">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 mr-2">
          <Filter className="w-3 h-3 text-zinc-500" />
          <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Severity</span>
        </div>
        {filters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => onFilterChange(filter.id)}
            className={cn(
              "px-4 py-1.5 rounded-full border text-[10px] font-mono uppercase tracking-widest transition-all duration-300",
              getColorClasses(filter.color, activeFilter === filter.id)
            )}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-zinc-900/40 border border-white/5 text-[10px] font-mono text-zinc-400 uppercase tracking-widest cursor-pointer hover:border-white/10 transition-colors">
          <span>Sort: Newest First</span>
          <ChevronDown className="w-3 h-3" />
        </div>
      </div>
    </div>
  );
}
