"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";
import { Terminal, Cpu, Eye, Zap, AlertTriangle, ShieldCheck } from "lucide-react";

interface NeuralMonologueProps {
  state: SimulationState;
  step: number;
  persona: string;
  logs?: string[];
  results?: any;
}

const LOG_DATA = [
  { type: "SYSTEM", icon: Cpu, color: "text-blue-400", text: "Initializing browser context. Target: orbitapparel.com/signup..." },
  { type: "VISION", icon: Eye, color: "text-emerald-400", text: "DOM loaded. Analyzing structure... Found primary form elements." },
  { type: "VISION", icon: Eye, color: "text-amber-400", text: "CTA contrast ratio check: 'Create Account' button vs. background - 1.2:1. WARNING: Below accessibility standards." },
  { type: "ACTION", icon: Zap, color: "text-purple-400", text: "Inputting email: testuser_specter@ai.net" },
  { type: "COGNITION", icon: Cpu, color: "text-emerald-400", text: "Analyzing field focus. User 'Power User' persona active. Expecting quick progression." },
  { type: "COGNITION", icon: AlertTriangle, color: "text-red-400", text: "[FRUSTRATION DETECTED] Confidence score dropping to 45%. No clear error validation visible." },
  { type: "ACTION", icon: Zap, color: "text-purple-400", text: "Pausing. Hovering over 'Create Account' button to trigger tooltip. No response." },
  { type: "STATUS", icon: ShieldCheck, color: "text-emerald-500", text: "AI Agent entering exploratory loop. Requesting human intervention." },
];

export function NeuralMonologue({ state, step, persona, logs = [], results }: NeuralMonologueProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentTime, setCurrentTime] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-US', { hour12: false }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, step]);

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Terminal Container */}
      <motion.div 
        initial={{ x: 50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="flex-1 rounded-[2rem] border border-white/5 bg-zinc-900/30 backdrop-blur-2xl overflow-hidden flex flex-col shadow-2xl"
      >
        {/* Terminal Header */}
        <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-white/5">
          <div className="flex items-center gap-3">
            <Terminal className="w-4 h-4 text-emerald-500" />
            <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-zinc-400">Neural Link: Internal Monologue</span>
          </div>
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-white/5 border border-white/10" />
            <div className="w-2.5 h-2.5 rounded-full bg-white/5 border border-white/10" />
            <div className="w-2.5 h-2.5 rounded-full bg-white/5 border border-white/10" />
          </div>
        </div>

        {/* Terminal Body */}
        <div 
          ref={containerRef}
          className="flex-1 p-6 font-mono text-xs overflow-y-auto scrollbar-hide space-y-4"
        >
          {state === "idle" && (
            <div className="h-full flex items-center justify-center text-zinc-600 italic">
              Waiting for link initialization...
            </div>
          )}

          {state === "scanning" && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-500">
                <span className="animate-pulse">{">"}</span>
                <span>Establishing secure tunnel to target...</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-500/60">
                <span className="animate-pulse">{">"}</span>
                <span>Calibrating vision sensors for persona: {persona.toUpperCase()}</span>
              </div>
            </div>
          )}

          {/* Real Logs from Backend */}
          <AnimatePresence>
            {logs.map((log, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="group flex gap-4 items-start border-l-2 border-transparent hover:border-emerald-500/30 pl-2 transition-colors duration-300"
              >
                <div className="flex-shrink-0 flex flex-col items-center pt-1">
                  <div className="w-6 h-6 rounded-lg bg-zinc-800 flex items-center justify-center border border-white/5 group-hover:scale-110 transition-transform text-emerald-400">
                    <Terminal className="w-3 h-3" />
                  </div>
                </div>
                
                <div className="flex-1 space-y-1">
                  <p className="text-zinc-300 leading-relaxed group-hover:text-white transition-colors text-xs">
                    {log}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Show test results when complete */}
          {results && state === "complete" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 rounded-lg bg-zinc-800/50 border border-emerald-500/30"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-500" />
                  <span className="font-bold text-emerald-500">Test Complete</span>
                </div>
                <div className="text-xs text-zinc-400 space-y-1">
                  <div>Status: <span className="text-white">{results.status || 'N/A'}</span></div>
                  {results.passed !== undefined && (
                    <div>Passed: <span className="text-white">{results.passed}/{results.passed + results.failed}</span></div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {state === "analyzing" && (
            <motion.div 
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="flex items-center gap-2 text-emerald-500/40 pl-2"
            >
              <span className="">_</span>
              <span className="text-[10px] uppercase tracking-widest italic">Thinking...</span>
            </motion.div>
          )}
        </div>

        {/* Terminal Footer Info */}
        <div className="px-6 py-3 border-t border-white/5 bg-black/20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Persona: {persona}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Confidence: {state === "idle" ? "0%" : "94.2%"}</span>
            </div>
          </div>
          <span className="text-[9px] text-zinc-700 uppercase tracking-widest">Encrypted Stream v4.2</span>
        </div>
      </motion.div>
    </div>
  );
}
