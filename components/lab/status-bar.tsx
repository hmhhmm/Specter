"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { SimulationState } from "@/app/lab/page";
import { Power, ShieldAlert, Cpu } from "lucide-react";

interface StatusBarProps {
  state: SimulationState;
  onTerminate: () => void;
}

export function StatusBar({ state, onTerminate }: StatusBarProps) {
  const [sessionTime, setSessionTime] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (state !== "idle") {
      interval = setInterval(() => {
        setSessionTime(prev => prev + 1);
      }, 1000);
    } else {
      setSessionTime(0);
    }
    return () => clearInterval(interval);
  }, [state]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <footer className="fixed bottom-0 left-0 right-0 h-10 bg-zinc-950/80 backdrop-blur-md border-t border-white/5 px-8 flex items-center justify-between z-50 overflow-hidden">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className={`w-1.5 h-1.5 rounded-full ${state !== "idle" ? "bg-emerald-500 animate-pulse" : "bg-zinc-700"}`} />
          <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest">
            Status: {state === "idle" ? "Ready" : state === "scanning" ? "Scanning" : state === "analyzing" ? "Analyzing" : "Complete"}
          </span>
        </div>
        
        <div className="h-3 w-px bg-white/10" />
        
        <div className="flex items-center gap-2">
          <Cpu className="w-3 h-3 text-zinc-600" />
          <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest">
            Processing: {state === "analyzing" ? "Active" : "Idle"}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-8">
        <div className="flex items-center gap-3">
          <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest leading-none">Session Time</span>
          <span className="text-[10px] font-mono text-white tracking-[0.2em]">{formatTime(sessionTime)}</span>
        </div>

        <button 
          onClick={onTerminate}
          className="group flex items-center gap-2 px-3 py-1 rounded bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 transition-colors"
        >
          <Power className="w-2.5 h-2.5 text-red-500 group-hover:scale-110 transition-transform" />
          <span className="text-[9px] font-mono text-red-500 uppercase tracking-widest">Terminate Session</span>
        </button>
      </div>
    </footer>
  );
}
