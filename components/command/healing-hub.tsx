"use client";

import { motion } from "framer-motion";
import { Cpu, Github, Terminal, ChevronRight, Sparkles } from "lucide-react";
import { GlowButton } from "@/components/ui/glow-button";

export function HealingHub() {
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
                <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-widest">Self-Healing Active</span>
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
            <span className="text-[8px] font-mono text-zinc-700 uppercase tracking-widest">trade-panel.tsx</span>
          </div>
          
          <div className="flex-1 bg-[#080808] rounded-2xl border border-white/5 p-5 font-mono text-[10px] leading-relaxed relative overflow-hidden flex flex-col group/code">
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
            
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              <div className="flex gap-4 opacity-40">
                <span className="w-4 shrink-0 text-right select-none">42</span>
                <p className="text-zinc-400">{"<input"}</p>
              </div>
              <div className="flex gap-4 bg-red-500/5 -mx-5 px-5 py-1 border-l-2 border-red-500/50">
                <span className="w-4 shrink-0 text-right text-red-500/40 select-none">43</span>
                <p className="text-red-400/90">-  type="text"</p>
              </div>
              <div className="flex gap-4 bg-emerald-500/10 -mx-5 px-5 py-1 border-l-2 border-emerald-500/50 relative">
                <span className="w-4 shrink-0 text-right text-emerald-500/40 select-none">44</span>
                <p className="text-emerald-500/90">+  type="text"</p>
              </div>
              <div className="flex gap-4 bg-emerald-500/10 -mx-5 px-5 py-1 border-l-2 border-emerald-500/50">
                <span className="w-4 shrink-0 text-right text-emerald-500/40 select-none">45</span>
                <p className="text-emerald-500/90">+  inputMode="decimal"</p>
                <motion.div 
                  initial={{ x: "-100%" }}
                  animate={{ x: "100%" }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 bg-emerald-500/5 w-1/4 skew-x-12 pointer-events-none"
                />
              </div>
              <div className="flex gap-4 opacity-40">
                <span className="w-4 shrink-0 text-right select-none">46</span>
                <p className="text-zinc-400">/&gt;</p>
              </div>
            </div>
            
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
              className="mt-6 p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/10 space-y-2"
            >
               <div className="flex items-center gap-2">
                 <Sparkles className="w-3 h-3 text-emerald-500" />
                 <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest font-bold">Vision Diagnosis</span>
               </div>
               <p className="text-[10px] text-zinc-500 leading-relaxed italic">
                 "Ghost Agent #0841 observed 8.2/10 friction score. Standard keyboard detected on currency input. Applying mobile input-mode patch."
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
