"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";
import { Terminal, Cpu, Eye, Zap, AlertTriangle, ShieldCheck, Globe } from "lucide-react";

interface NeuralMonologueProps {
  state: SimulationState;
  step: number;
  persona: string;
  objective: string;
}

const LOG_DATA = [
  { type: "SYSTEM", icon: Cpu, color: "text-blue-400", text: "Initializing browser context. Target: novatrade.io/dashboard..." },
  { type: "VISION", icon: Eye, color: "text-emerald-400", text: "Viewport: Mobile (390x844). Analyzing z-index stack... [CRITICAL] Chat widget z-9999 overlapping 'Sell' button." },
  { type: "COGNITION", icon: AlertTriangle, color: "text-red-400", text: "Data Overflow detected. BTC Price '$10,420.50' exceeds container width. Text clipped at viewport edge." },
  { type: "VISION", icon: Eye, color: "text-amber-400", text: "Contrast check: 'Transaction Fee: $2.50' - Fee VALUE invisible. Color #0a0a0c on #0a0a0c background." },
  { type: "ACTION", icon: Zap, color: "text-purple-400", text: "Tapping 'Amount' input. Mobile keyboard: ABC triggered. Expected: numeric keypad (123). UX friction: HIGH." },
  { type: "COGNITION", icon: Globe, color: "text-emerald-400", text: "Switching language to DE. Button 'Handel bestätigen' exceeds fixed 180px container. Text clipped." },
  { type: "ACTION", icon: Zap, color: "text-purple-400", text: "Executing 'Withdraw' intent. Click registered. No state change. No error message. Silent failure confirmed." },
  { type: "STATUS", icon: ShieldCheck, color: "text-emerald-500", text: "[TERMINAL] Global loading spinner activated. UI locked. All interactions blocked. Session terminated." },
];

export function NeuralMonologue({
  state,
  step,
  persona,
  objective,
}: NeuralMonologueProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentTime, setCurrentTime] = useState("");

  const dynamicLogs = [
    {
      type: "SYSTEM",
      icon: Cpu,
      color: "text-blue-400",
      text: `Objective Received: "${objective}"`,
    },
    ...LOG_DATA.slice(1),
  ];

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
  }, [step]);

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
          className="flex-1 p-4 font-mono text-[11px] overflow-y-auto scrollbar-hide space-y-3"
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

          <AnimatePresence>
            {dynamicLogs.slice(0, step).map((log, i) => {
              const Icon = log.icon;
              return (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="group flex gap-3 items-start border-l-2 border-transparent hover:border-emerald-500/30 pl-2 transition-colors duration-300"
                >
                  <div className="flex-shrink-0 flex flex-col items-center pt-0.5">
                    <div className={cn("w-5 h-5 rounded-md bg-zinc-800 flex items-center justify-center border border-white/5 group-hover:scale-110 transition-transform", log.color)}>
                      <Icon className="w-2.5 h-2.5" />
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-[8px] text-zinc-600">[{currentTime}]</span>
                      <span className={cn("text-[8px] font-bold uppercase tracking-widest", log.color)}>{log.type}</span>
                    </div>
                    <p className="text-zinc-300 leading-normal group-hover:text-white transition-colors">
                      {log.text}
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {state === "analyzing" && step < dynamicLogs.length && (
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
