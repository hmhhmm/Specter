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
    <footer className="fixed bottom-0 left-0 right-0 h-12 bg-white/90 dark:bg-zinc-950/90 backdrop-blur-md border-t border-zinc-200 dark:border-white/5 px-6 flex items-center justify-between z-50 transition-colors duration-300">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`w-1.5 h-1.5 rounded-full ${state !== "idle" ? "bg-emerald-500 animate-pulse" : "bg-zinc-300 dark:bg-zinc-700"}`} />
          <span className="text-[10px] font-mono text-zinc-500 dark:text-zinc-500 uppercase tracking-wider">
            {state === "idle" ? "Ready" : state === "scanning" ? "Scanning" : state === "analyzing" ? "Analyzing" : "Complete"}
          </span>
        </div>
        
        <div className="h-3 w-px bg-zinc-200 dark:bg-white/10" />
        
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-zinc-400 dark:text-zinc-600 uppercase tracking-wider">Session</span>
          <span className="text-[11px] font-mono text-zinc-900 dark:text-white">{formatTime(sessionTime)}</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button 
          onClick={onTerminate}
          className="group flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 transition-colors"
        >
          <Power className="w-3 h-3 text-red-500" />
          <span className="text-[10px] font-mono text-red-500 uppercase tracking-wider">Terminate</span>
        </button>
      </div>
    </footer>
  );
}
