"use client";

import { motion } from "framer-motion";
import { GitBranch, TrendingUp, AlertCircle, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface Pattern {
  pattern_id: string;
  error_type: string;
  component: string;
  occurrences: number;
  test_runs: string[];
  team: string;
}

export function RootCausePanel() {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatterns();
  }, []);

  const fetchPatterns = async () => {
    try {
      const response = await fetch('/api/root-cause/patterns');
      const data = await response.json();
      setPatterns(data.patterns || []);
    } catch (error) {
      console.error('Error fetching patterns:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="animate-pulse text-zinc-600 text-sm">Analyzing patterns...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {patterns.length === 0 ? (
        <div className="text-center text-zinc-600 text-sm py-8">
          No recurring patterns detected yet
        </div>
      ) : (
        patterns.slice(0, 5).map((pattern, index) => (
          <motion.div
            key={pattern.pattern_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-emerald-500/30 transition-all duration-300 group"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <GitBranch className="w-4 h-4 text-emerald-500" />
                <span className="text-xs font-mono text-emerald-400">
                  {pattern.component.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className={cn(
                  "w-3 h-3",
                  pattern.occurrences >= 5 ? "text-red-500" :
                  pattern.occurrences >= 3 ? "text-amber-500" :
                  "text-blue-500"
                )} />
                <span className="text-xs font-bold text-zinc-400">
                  {pattern.occurrences}x
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-3 h-3 text-zinc-600" />
                <span className="text-[10px] text-zinc-500 uppercase tracking-widest">
                  {pattern.error_type.replace('_', ' ')}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Users className="w-3 h-3 text-zinc-600" />
                <span className="text-[10px] text-zinc-500">
                  Assigned to: <span className="text-emerald-500">{pattern.team}</span>
                </span>
              </div>

              <div className="flex gap-1 flex-wrap mt-2">
                {pattern.test_runs.slice(0, 3).map((run, i) => (
                  <div
                    key={i}
                    className="px-2 py-0.5 rounded bg-zinc-800/50 text-[8px] text-zinc-600 font-mono"
                  >
                    {run.split('_').slice(-2).join('-')}
                  </div>
                ))}
                {pattern.test_runs.length > 3 && (
                  <div className="px-2 py-0.5 rounded bg-zinc-800/50 text-[8px] text-zinc-600 font-mono">
                    +{pattern.test_runs.length - 3}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))
      )}
    </div>
  );
}
