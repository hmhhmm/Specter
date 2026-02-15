"use client";

import { motion } from "framer-motion";
import { SpecterNav } from "@/components/landing/specter-nav";
import { IntelligencePanel } from "@/components/command/intelligence-panel";
import { RevenueEpicenter } from "@/components/command/revenue-epicenter";
import { HealingHub } from "@/components/command/healing-hub";

export default function CommandPage() {
  return (
    <main className="relative min-h-screen bg-white dark:bg-[#050505] text-zinc-900 dark:text-white overflow-hidden selection:bg-emerald-500/30 transition-colors duration-300">
      {/* Ambient Effects - Consistent with Lab/Vault */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden opacity-[0.02] dark:opacity-[0.03]">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-100 contrast-150"></div>
      </div>
      <div className="fixed inset-0 pointer-events-none z-50 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(0,255,0,0.03),rgba(0,255,0,0.01),rgba(0,0,255,0.03))] bg-[length:100%_4px,3px_100%] opacity-5 dark:opacity-20"></div>

      {/* Background Decorative Grid */}
      <div className="fixed inset-0 z-0 opacity-[0.03] dark:opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>
      </div>

      {/* Page Content */}
      <div className="relative z-10 flex flex-col h-screen">
        <SpecterNav />

        <div className="flex-1 px-8 py-6 max-w-[1650px] mx-auto w-full overflow-hidden mt-20">
          <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr_340px] gap-6 h-full max-h-full">
            {/* Left Panel */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="h-full overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-zinc-300 dark:scrollbar-thumb-zinc-700 scrollbar-track-transparent"
            >
              <IntelligencePanel />
            </motion.div>

            {/* Center Panel */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="h-full overflow-hidden"
            >
              <RevenueEpicenter />
            </motion.div>

            {/* Right Panel */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="h-full overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-zinc-300 dark:scrollbar-thumb-zinc-700 scrollbar-track-transparent"
            >
              <HealingHub />
            </motion.div>
          </div>
        </div>
      </div>
    </main>
  );
}
