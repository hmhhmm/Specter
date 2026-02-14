"use client";

import { motion } from "framer-motion";
import { Activity, Ghost, Database, Wifi, Signal, Clock } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

interface MissionHeaderProps {
  activePersona?: string;
  networkCondition?: string;
  nextTestIn?: number; // seconds until next test
}

export function MissionHeader({ activePersona, networkCondition, nextTestIn }: MissionHeaderProps = {}) {
  const [countdown, setCountdown] = useState(nextTestIn || 0);

  useEffect(() => {
    if (nextTestIn !== undefined) {
      setCountdown(nextTestIn);
    }
  }, [nextTestIn]);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setInterval(() => {
        setCountdown((prev) => Math.max(0, prev - 1));
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [countdown]);

  const personaEmoji: Record<string, string> = {
    zoomer: "⚡",
    boomer: "👵",
    skeptic: "🕵️",
    chaos: "💥",
    mobile: "📱"
  };

  const networkIcons: Record<string, any> = {
    wifi: Wifi,
    "4g": Signal,
    "3g": Signal
  };

  const NetworkIcon = networkCondition ? networkIcons[networkCondition] : Wifi;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <header className="relative w-full border-b border-zinc-200 dark:border-white/5 bg-white/50 dark:bg-zinc-950/50 backdrop-blur-xl px-8 py-4 flex items-center justify-between z-20 transition-colors duration-300">
      <div className="flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2 group transition-opacity hover:opacity-80">
          <span className="font-bricolage text-lg font-bold tracking-tight text-zinc-900 dark:text-white">
            Specter
          </span>
        </Link>
        
        <div className="h-4 w-px bg-zinc-200 dark:bg-white/10 hidden md:block" />
        
        <div className="hidden md:flex items-center gap-6 text-[10px] font-mono text-zinc-500 dark:text-zinc-500 uppercase tracking-widest">
          <Link href="/lab" className="hover:text-emerald-500 transition-colors">Lab</Link>
          <Link href="/vault" className="flex items-center gap-2 hover:text-emerald-500 transition-colors">
            <Database className="w-3 h-3" />
            Vault
          </Link>
          <Link href="/command" className="hover:text-emerald-500 transition-colors">Command</Link>
        </div>

        {countdown > 0 && (
          <>
            <div className="h-4 w-px bg-zinc-200 dark:bg-white/10 hidden md:block" />
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <Clock className="w-3 h-3 text-blue-400" />
              <span className="text-xs text-blue-400 font-mono">
                Next test in {formatTime(countdown)}
              </span>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
