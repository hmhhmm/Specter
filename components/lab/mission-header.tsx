"use client";

import { motion } from "framer-motion";
import { Activity, Ghost, Database } from "lucide-react";
import Link from "next/link";

export function MissionHeader() {
  return (
    <header className="relative w-full border-b border-white/5 bg-zinc-950/50 backdrop-blur-xl px-8 py-4 flex items-center justify-between z-20">
      <div className="flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2 group transition-opacity hover:opacity-80">
          <Ghost className="w-5 h-5 text-emerald-500 group-hover:scale-110 transition-transform" />
          <span className="font-bricolage text-lg font-bold tracking-tight text-white uppercase">
            Specter.AI
          </span>
        </Link>
        
        <div className="h-4 w-px bg-white/10 hidden md:block" />
        
        <div className="hidden md:flex items-center gap-6 text-[10px] font-mono text-zinc-500 uppercase tracking-widest">
          <Link href="/lab" className="hover:text-emerald-500 transition-colors">Lab</Link>
          <Link href="/vault" className="flex items-center gap-2 hover:text-emerald-500 transition-colors">
            <Database className="w-3 h-3" />
            Vault
          </Link>
          <Link href="/command" className="hover:text-emerald-500 transition-colors">Command</Link>
        </div>

        <div className="h-4 w-px bg-white/10 hidden md:block" />
        
        <div className="flex items-center gap-3">
          <div className="relative flex h-2 w-2">
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </div>
          <h1 className="font-mono text-xs tracking-[0.2em] text-zinc-400 uppercase">
            Active Session
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-8">

        <div className="px-3 py-1 rounded-md border border-white/10 bg-white/5 flex items-center gap-2">
          <Activity className="w-3 h-3 text-emerald-500" />
          <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-widest">Live</span>
        </div>
      </div>
    </header>
  );
}
