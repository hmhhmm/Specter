"use client";

import { Ghost } from "lucide-react";
import Link from "next/link";

export function MissionHeader() {
  return (
    <header className="relative w-full border-b border-white/5 bg-zinc-950/50 backdrop-blur-xl px-8 py-4 flex items-center justify-between z-20">
      <div className="flex items-center gap-6">
        <Link href="/">
          <span className="font-bricolage text-lg font-bold tracking-tight text-white uppercase">
            Specter
          </span>
        </Link>
        
        <div className="h-4 w-px bg-white/10" />
        
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
          <h1 className="font-mono text-xs tracking-[0.2em] text-zinc-400 uppercase">
            Autonomous Testing Lab
          </h1>
        </div>
      </div>
    </header>
  );
}
