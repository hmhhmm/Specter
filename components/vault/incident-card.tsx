"use client";

import { motion } from "framer-motion";
import { EvidencePreview } from "./evidence-preview";
import { cn } from "@/lib/utils";
import { Target, AlertTriangle, Smartphone, Terminal, ChevronRight, Lock, Eye, Cpu } from "lucide-react";
import { useState } from "react";

export interface Incident {
  id: string;
  severity: string;
  title: string;
  type: "z-index" | "overflow" | "contrast" | "keyboard" | "i18n" | "phantom" | "dead-end";
  device: string;
  confidence: number;
  revenueLoss: number;
  cloudPosition: { x: number; y: number };
  monologue: string;
  remediation: string;
}

interface IncidentCardProps {
  incident: Incident;
  index: number;
}

export function IncidentCard({ incident, index }: IncidentCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  const isP0 = incident.severity === "P0";

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div 
      className={cn(
        "relative h-full min-h-[500px] [perspective:1000px] cursor-pointer group",
        isP0 && "lg:col-span-2"
      )}
      onClick={handleFlip}
    >
      <motion.div
        initial={false}
        animate={{ rotateY: isFlipped ? 180 : 0 }}
        transition={{ 
          duration: 0.8, 
          type: "spring", 
          stiffness: 260, 
          damping: 20 
        }}
        className="relative w-full h-full [transform-style:preserve-3d]"
      >
        {/* FRONT FACE */}
        <div 
          className="absolute inset-0 [backface-visibility:hidden] [transform:translateZ(1px)]"
          style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}
            className={cn(
              "relative p-6 rounded-[2rem] bg-zinc-900/40 border border-white/5 hover:border-white/10 transition-all duration-500 overflow-hidden flex flex-col h-full [backface-visibility:hidden]"
            )}
          >
            {/* Background Glow */}
            <div className={cn(
              "absolute -top-24 -right-24 w-64 h-64 blur-[80px] opacity-10 pointer-events-none group-hover:opacity-20 transition-opacity duration-500",
              isP0 ? "bg-red-500" : "bg-emerald-500"
            )} />

            <div className="relative z-10 flex flex-col h-full">
              <div className="flex items-center justify-between mb-6">
                <div className={cn(
                  "px-3 py-1 rounded-full border text-[9px] font-mono uppercase tracking-widest",
                  incident.severity === "P0" ? "bg-red-500/10 border-red-500/30 text-red-400" :
                  incident.severity === "P1" ? "bg-amber-500/10 border-amber-500/30 text-amber-400" :
                  incident.severity === "P2" ? "bg-yellow-500/10 border-yellow-500/30 text-yellow-400" :
                  "bg-blue-500/10 border-blue-500/30 text-blue-400"
                )}>
                  {incident.severity} Critical
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">Case #{incident.id}</span>
                  <div className="w-1 h-1 rounded-full bg-zinc-700" />
                  <span className="text-[10px] font-mono text-emerald-500/60 uppercase tracking-widest group-hover:text-emerald-500 transition-colors">Decrypting...</span>
                </div>
              </div>

              <h3 className={cn(
                "font-bricolage font-bold tracking-tight text-white mb-2 transition-transform duration-500 group-hover:translate-x-1",
                isP0 ? "text-3xl" : "text-xl"
              )}>
                {incident.title}
              </h3>

              <div className="flex items-center gap-2 mb-6 text-zinc-500">
                <Smartphone className="w-3 h-3" />
                <span className="text-[10px] font-mono uppercase tracking-widest">{incident.device}</span>
                <span className="mx-2 opacity-20">|</span>
                <span className="text-[10px] font-mono uppercase tracking-widest italic opacity-50">Click to flip</span>
              </div>

              <div className="mb-6">
                <EvidencePreview 
                  cloudPosition={incident.cloudPosition} 
                  type={incident.type}
                />
              </div>

              <div className="mt-auto pt-4 border-t border-white/5 grid grid-cols-2 gap-4">
                <div className="flex flex-col">
                  <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">AI Confidence</span>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 bg-zinc-800 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${incident.confidence}%` }}
                        transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
                        className="h-full bg-emerald-500"
                      />
                    </div>
                    <span className="text-xs font-mono text-emerald-500">{incident.confidence}%</span>
                  </div>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Revenue Impact</span>
                  <div className="flex items-center gap-1.5">
                    <AlertTriangle className="w-3 h-3 text-red-500" />
                    <span className="text-sm font-bold font-bricolage text-red-500">
                      -${incident.revenueLoss.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* BACK FACE */}
        <div 
          className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)_translateZ(1px)]"
          style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}
        >
          <div 
            style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}
            className={cn(
              "relative p-8 rounded-[2rem] bg-[#0A0A0A] border border-emerald-500/20 transition-all duration-500 overflow-hidden flex flex-col h-full shadow-[0_0_30px_rgba(16,185,129,0.05)] [backface-visibility:hidden]"
            )}
          >
            {/* Background Grid Pattern */}
            <div className="absolute inset-0 opacity-10 pointer-events-none bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:20px_20px]" />
            
            {/* Glow Accent */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-3xl pointer-events-none" />

            <div className="relative z-10 flex flex-col h-full">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <Terminal className="w-4 h-4 text-emerald-500" />
                  </div>
                  <div>
                    <h4 className="text-[10px] font-mono text-emerald-500 uppercase tracking-widest leading-none mb-1">Neural Monologue</h4>
                    <div className="flex items-center gap-1.5">
                      <Lock className="w-2.5 h-2.5 text-zinc-600" />
                      <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-widest">Decrypted Session #{incident.id}</span>
                    </div>
                  </div>
                </div>
                <div className="px-2 py-0.5 rounded border border-emerald-500/30 text-[8px] font-mono text-emerald-500 uppercase tracking-widest animate-pulse">
                  Active Link
                </div>
              </div>

              <div className="flex-1 font-mono text-xs leading-relaxed text-zinc-400 overflow-y-auto pr-2 custom-scrollbar">
                <div className="flex gap-3 mb-4">
                  <span className="text-emerald-500 shrink-0 opacity-50">01</span>
                  <p><span className="text-emerald-400/80">system.audit(</span><span className="text-zinc-500">"{incident.title}"</span><span className="text-emerald-400/80">)</span></p>
                </div>
                
                <div className="flex gap-3 mb-6">
                  <span className="text-emerald-500 shrink-0 opacity-50">02</span>
                  <div className="space-y-4">
                    <p className="text-zinc-300 leading-relaxed italic">
                      {">"} "{incident.monologue}"
                    </p>
                    
                    <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
                      <div className="flex items-center gap-2">
                        <Eye className="w-3 h-3 text-amber-500" />
                        <span className="text-[9px] uppercase tracking-widest text-amber-500/80 font-bold">Recommended Fix</span>
                      </div>
                      <p className="text-[10px] text-zinc-400 leading-relaxed">
                        {incident.remediation}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <span className="text-emerald-500 shrink-0 opacity-50">03</span>
                  <p className="flex items-center gap-2">
                    <Cpu className="w-3 h-3 text-emerald-500" />
                    <span className="text-emerald-500/80">Simulation terminated. Recommendation: Deploy UI patch v2.1.</span>
                  </p>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <button className="flex items-center gap-2 text-[10px] font-mono text-zinc-500 uppercase tracking-widest hover:text-emerald-500 transition-colors group/btn">
                    <span>Export Logs</span>
                    <ChevronRight className="w-3 h-3 group-hover/btn:translate-x-1 transition-transform" />
                  </button>
                </div>
                <button 
                  className="px-4 py-2 rounded-lg bg-emerald-500 text-black font-mono text-[10px] font-bold uppercase tracking-widest hover:bg-emerald-400 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                  onClick={(e) => { e.stopPropagation(); handleFlip(); }}
                >
                  Return to Link
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
