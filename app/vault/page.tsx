"use client";

import { motion } from "framer-motion";
import { VaultHeader } from "@/components/vault/vault-header";
import { VaultFilters } from "@/components/vault/vault-filters";
import { IncidentGrid } from "@/components/vault/incident-grid";
import { SpecterNav } from "@/components/landing/specter-nav";
import { StatusBar } from "@/components/lab/status-bar";
import { useState } from "react";

export default function VaultPage() {
  const [activeFilter, setActiveFilter] = useState("all");

  return (
    <main className="relative min-h-screen bg-[#050505] text-white overflow-hidden selection:bg-red-500/30">
      {/* Ambient Effects - Consistent with Lab */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden opacity-[0.03]">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-100 contrast-150"></div>
      </div>
      <div className="fixed inset-0 pointer-events-none z-50 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.03),rgba(0,255,0,0.01),rgba(0,0,255,0.03))] bg-[length:100%_4px,3px_100%] pointer-events-none opacity-20"></div>

      {/* Page Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <SpecterNav />

        <div className="flex-1 px-8 py-12 max-w-7xl mx-auto w-full mb-20 mt-20">
          <VaultHeader />
          <VaultFilters
            activeFilter={activeFilter}
            onFilterChange={setActiveFilter}
          />
          <IncidentGrid activeFilter={activeFilter} />
        </div>

        <StatusBar
          state="idle"
          onTerminate={() => (window.location.href = "/")}
        />
      </div>

      {/* Background Decorative Grid */}
      <div className="fixed inset-0 z-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>
      </div>
    </main>
  );
}
