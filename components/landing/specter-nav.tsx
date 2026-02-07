"use client";

import { motion } from "framer-motion";
import { Ghost, ScanSearch, Database } from "lucide-react";
import Link from "next/link";
import { GlowButton } from "@/components/ui/glow-button";

export function SpecterNav() {
  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: "circOut" }}
      className="fixed top-0 left-0 right-0 z-50 flex justify-center p-6"
    >
      <div className="flex items-center justify-between w-full max-w-7xl px-6 py-3 bg-zinc-950/40 backdrop-blur-xl border border-zinc-800 rounded-full">
        <Link href="/" className="flex items-center gap-2 group transition-opacity hover:opacity-80">
          <Ghost className="w-6 h-6 text-emerald-500 group-hover:scale-110 transition-transform" />
          <span className="font-bricolage text-xl font-bold tracking-tight text-white">
            Specter.AI
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8 text-zinc-400 font-mono text-sm">
          <Link href="#features" className="hover:text-emerald-500 transition-colors">Features</Link>
          <Link href="/vault" className="flex items-center gap-2 hover:text-emerald-500 transition-colors">
            <Database className="w-4 h-4" />
            Vault
          </Link>
          <Link href="#docs" className="hover:text-emerald-500 transition-colors">Docs</Link>
        </div>

        <div className="flex items-center gap-4">
          <button className="text-zinc-400 font-mono text-sm hover:text-white transition-colors">
            Login
          </button>
          <Link href="/lab">
            <GlowButton className="px-4 py-2 text-sm">
              Launch
            </GlowButton>
          </Link>
        </div>
      </div>
    </motion.nav>
  );
}
