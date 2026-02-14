"use client";

import { useEffect, useState } from "react";
import { SpecterNav } from "@/components/landing/specter-nav";
import { StatusBar } from "@/components/lab/status-bar";
import { AIBriefing } from "@/components/command/ai-briefing";
import { IntelligencePanel } from "@/components/command/intelligence-panel";
import { RevenueEpicenter } from "@/components/command/revenue-epicenter";
import { HealingHub } from "@/components/command/healing-hub";
import { RootCausePanel } from "@/components/command/root-cause-panel";
import { RegionalMap } from "@/components/command/regional-map";
import { CompetitorBar } from "@/components/command/competitor-bar";
import { FScoreWave } from "@/components/command/f-score-wave";

export default function CommandPage() {
  const [stats, setStats] = useState({
    totalTests: 0,
    issuesFound: 0,
    uptime: "0%",
    revenueLoss: 0
  });

  useEffect(() => {
    // Connect to WebSocket for live stats
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("Command dashboard connected to backend");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Update stats based on incoming events
        if (data.type === "stats_update") {
          setStats({
            totalTests: data.totalTests || 0,
            issuesFound: data.issuesFound || 0,
            uptime: data.uptime || "0%",
            revenueLoss: data.revenueLoss || 0
          });
        } else if (data.type === "test_complete") {
          // Increment total tests and calculate revenue loss
          setStats(prev => ({
            ...prev,
            totalTests: prev.totalTests + 1,
            issuesFound: prev.issuesFound + (data.results?.failed || 0),
            revenueLoss: prev.revenueLoss + ((data.results?.failed || 0) * 15000) // $15k per critical issue
          }));
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("Command WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("Command WebSocket disconnected");
    };

    return () => {
      ws.close();
    };
  }, []);
  return (
    <main className="relative min-h-screen bg-white dark:bg-[#050505] text-zinc-900 dark:text-white overflow-hidden selection:bg-emerald-500/30 transition-colors duration-300">
      {/* Grain overlay */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden opacity-[0.03] dark:opacity-[0.03]">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-100 contrast-150"></div>
      </div>

      {/* Scanline effect */}
      <div className="fixed inset-0 pointer-events-none z-50 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%)] dark:bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_4px] opacity-5 dark:opacity-20"></div>

      {/* Background grid */}
      <div className="fixed inset-0 z-0 opacity-[0.03] dark:opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>
      </div>

      {/* Page Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <SpecterNav />

        <div className="flex-1 px-8 py-12 max-w-[1600px] mx-auto w-full mb-20 mt-28">
          <AIBriefing 
            totalTests={stats.totalTests}
            issuesFound={stats.issuesFound}
            uptime={stats.uptime}
            revenueLoss={stats.revenueLoss}
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
            <IntelligencePanel />
            <RevenueEpicenter />
            <HealingHub />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <RootCausePanel />
            <RegionalMap />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <CompetitorBar />
            <FScoreWave />
          </div>
        </div>

        <StatusBar
          state="complete"
          onTerminate={() => (window.location.href = "/")}
        />
      </div>
    </main>
  );
}
