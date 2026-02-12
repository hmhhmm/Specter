"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Cpu, Github, Terminal, ChevronRight, Sparkles } from "lucide-react";
import { GlowButton } from "@/components/ui/glow-button";

interface HealingSuggestion {
  id: string;
  file: string;
  type: string;
  description: string;
  code_before: string;
  code_after: string;
  impact: string;
}

export function HealingHub() {
  const [suggestion, setSuggestion] = useState<HealingSuggestion | null>(null);
  const [loading, setLoading] = useState(true);
  const [heuristicText, setHeuristicText] = useState("Observed 4 rage-click events per session on mobile viewports. Primary cause: low-contrast visibility. Applying perceptual lift.");

  useEffect(() => {
    async function fetchSuggestions() {
      try {
        const response = await fetch("http://localhost:8000/api/healing/suggestions");
        if (response.ok) {
          const data = await response.json();
          if (data.suggestions && data.suggestions.length > 0) {
            setSuggestion(data.suggestions[0]);
            setHeuristicText(data.suggestions[0].impact + ". " + data.suggestions[0].description);
          }
        }
      } catch (err) {
        console.error("Error fetching healing suggestions:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchSuggestions();
  }, []);

  const displayFile = suggestion?.file || "globals.css";
  const codeBefore = suggestion?.code_before || ".checkout-button {\n  color: var(--gray-mute);\n}";
  const codeAfter = suggestion?.code_after || ".checkout-button {\n  color: var(--emerald-glow);\n  box-shadow: 0 0 20px rgba(16,185,129,0.2);\n}";

  // Parse code lines for display
  const beforeLines = codeBefore.split("\n");
  const afterLines = codeAfter.split("\n");

  return (
    <div className="flex flex-col gap-6 h-full">
      {/* Autonomous Remediation Card */}
      <div className="rounded-[2.5rem] bg-zinc-900/40 border border-emerald-500/10 p-6 flex flex-col flex-1 relative overflow-hidden group shadow-lg">
        {/* Glow Accent */}
        <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/5 blur-3xl pointer-events-none group-hover:bg-emerald-500/10 transition-colors duration-700" />
        
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center relative">
              <Cpu className="w-5 h-5 text-emerald-500" />
              <motion.div 
                animate={{ opacity: [0, 1, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute inset-0 bg-emerald-500/20 blur-md rounded-xl"
              />
            </div>
            <div>
              <h4 className="text-[11px] font-mono text-emerald-500 uppercase tracking-widest leading-none mb-1 font-bold">Autonomous Remediation</h4>
              <div className="flex items-center gap-1.5">
                <div className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-widest">{loading ? "Analyzing..." : "Self-Healing Active"}</span>
              </div>
            </div>
          </div>
          <div className="px-2.5 py-1 rounded-md border border-emerald-500/30 bg-emerald-500/5 text-[9px] font-mono text-emerald-500 uppercase tracking-[0.2em] font-bold">
            v1.0.4
          </div>
        </div>

        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Terminal className="w-3 h-3 text-zinc-500" />
              <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest font-bold">Proposed Patch</span>
            </div>
            <span className="text-[8px] font-mono text-zinc-700 uppercase tracking-widest">{displayFile}</span>
          </div>
          
          <div className="flex-1 bg-[#080808] rounded-2xl border border-white/5 p-5 font-mono text-[10px] leading-relaxed relative overflow-hidden flex flex-col group/code">
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
            
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              {beforeLines.map((line, i) => (
                <div key={`before-${i}`} className="flex gap-4 bg-red-500/5 -mx-5 px-5 py-1 border-l-2 border-red-500/50">
                  <span className="w-4 shrink-0 text-right text-red-500/40 select-none">{i + 1}</span>
                  <p className="text-red-400/90">- {line}</p>
                </div>
              ))}
              {afterLines.map((line, i) => (
                <div key={`after-${i}`} className="flex gap-4 bg-emerald-500/10 -mx-5 px-5 py-1 border-l-2 border-emerald-500/50 relative">
                  <span className="w-4 shrink-0 text-right text-emerald-500/40 select-none">{beforeLines.length + i + 1}</span>
                  <p className="text-emerald-500/90">+ {line}</p>
                  {i === 0 && (
                    <motion.div 
                      initial={{ x: "-100%" }}
                      animate={{ x: "100%" }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                      className="absolute inset-0 bg-emerald-500/5 w-1/4 skew-x-12 pointer-events-none"
                    />
                  )}
                </div>
              ))}
            </div>
            
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
              className="mt-6 p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/10 space-y-2"
            >
               <div className="flex items-center gap-2">
                 <Sparkles className="w-3 h-3 text-emerald-500" />
                 <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest font-bold">Heuristic Analysis</span>
               </div>
               <p className="text-[10px] text-zinc-500 leading-relaxed italic">
                 "{heuristicText}"
               </p>
            </motion.div>
          </div>
        </div>

        <div className="mt-8 space-y-3">
          <GlowButton className="w-full py-5 text-[10px] tracking-[0.2em] uppercase flex items-center justify-center gap-3 font-bold group/btn">
            <Github className="w-4 h-4 group-hover/btn:scale-110 transition-transform" />
            Open GitHub Pull Request
          </GlowButton>
          
          <button className="w-full py-3.5 rounded-xl border border-white/5 bg-white/5 text-[9px] font-mono text-zinc-500 uppercase tracking-widest hover:text-white hover:bg-white/10 hover:border-white/10 transition-all flex items-center justify-center gap-2 group/audit">
            <span>View Full Impact Audit</span>
            <ChevronRight className="w-3 h-3 group-hover/audit:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </div>
  );
}
