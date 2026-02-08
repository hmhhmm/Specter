"use client";

import { useEffect, useState } from "react";
import { SimulationState } from "@/app/lab/page";
import { Power } from "lucide-react";

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
    <footer className="fixed bottom-0 left-0 right-0 h-8 bg-zinc-950/90 backdrop-blur-md border-t border-white/5 px-6 flex items-center justify-between z-50">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`w-1.5 h-1.5 rounded-full ${state !== "idle" ? "bg-emerald-500" : "bg-zinc-700"}`} />
          <span className="text-[9px] font-mono text-zinc-500 uppercase">
            {state === "idle" ? "Ready" : state === "scanning" ? "Scanning" : state === "analyzing" ? "Analyzing" : "Complete"}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-[9px] font-mono text-white">{formatTime(sessionTime)}</span>
        <button 
          onClick={onTerminate}
          className="flex items-center gap-1.5 px-2 py-1 rounded bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 transition-colors"
        >
          <Power className="w-2.5 h-2.5 text-red-500" />
          <span className="text-[9px] font-mono text-red-500 uppercase">Stop</span>
        </button>
      </div>
    </footer>
  );
}
