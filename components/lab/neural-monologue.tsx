"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";
import { Terminal, Cpu, Eye, Zap, AlertTriangle, ShieldCheck, Network, Activity, GitBranch } from "lucide-react";

interface NeuralMonologueProps {
  state: SimulationState;
  step: number;
  persona: string;
  logs?: string[];
  results?: any;
  currentStepData?: any;
}

export function NeuralMonologue({ state, step, persona, logs = [], results, currentStepData }: NeuralMonologueProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentTime, setCurrentTime] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-US', { hour12: false }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, step, currentStepData]);

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Terminal Container */}
      <motion.div 
        initial={{ x: 50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="flex-1 rounded-[2rem] border border-white/5 bg-zinc-900/30 backdrop-blur-2xl overflow-hidden flex flex-col shadow-2xl"
      >
        {/* Terminal Header */}
        <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-white/5">
          <div className="flex items-center gap-3">
            <Terminal className="w-4 h-4 text-emerald-500" />
            <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-zinc-400">Neural Link: Internal Monologue</span>
          </div>
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-white/5 border border-white/10" />
            <div className="w-2.5 h-2.5 rounded-full bg-white/5 border border-white/10" />
            <div className="w-2.5 h-2.5 rounded-full bg-white/5 border border-white/10" />
          </div>
        </div>

        {/* Terminal Body */}
        <div 
          ref={containerRef}
          className="flex-1 p-6 font-mono text-xs overflow-y-scroll space-y-4"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: '#4ade80 #18181b'
          }}
        >
          {state === "idle" && (
            <div className="h-full flex items-center justify-center text-zinc-600 italic">
              Waiting for link initialization...
            </div>
          )}

          {state === "scanning" && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-500">
                <span className="animate-pulse">{">"}</span>
                <span>Establishing secure tunnel to target...</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-500/60">
                <span className="animate-pulse">{">"}</span>
                <span>Calibrating vision sensors for persona: {persona.toUpperCase()}</span>
              </div>
            </div>
          )}

          {/* Real Logs from Backend */}
          <AnimatePresence>
            {logs.map((log, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="group flex gap-4 items-start border-l-2 border-transparent hover:border-emerald-500/30 pl-2 transition-colors duration-300"
              >
                <div className="flex-shrink-0 flex flex-col items-center pt-1">
                  <div className="w-6 h-6 rounded-lg bg-zinc-800 flex items-center justify-center border border-white/5 group-hover:scale-110 transition-transform text-emerald-400">
                    <Terminal className="w-3 h-3" />
                  </div>
                </div>
                
                <div className="flex-1 space-y-1">
                  <p className="text-zinc-300 leading-relaxed group-hover:text-white transition-colors text-xs">
                    {log}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Comprehensive Diagnostic Panel */}
          {currentStepData && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 rounded-xl bg-gradient-to-br from-zinc-800/80 to-zinc-900/80 border border-emerald-500/30 shadow-2xl"
            >
              {/* Header with Severity & Team */}
              <div className="flex items-start justify-between mb-3 pb-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <AlertTriangle className={cn(
                    "w-5 h-5",
                    currentStepData.severity?.includes('P0') && "text-red-500",
                    currentStepData.severity?.includes('P1') && "text-orange-500",
                    currentStepData.severity?.includes('P2') && "text-yellow-500",
                    currentStepData.severity?.includes('P3') && "text-blue-500",
                    !currentStepData.severity && "text-emerald-500"
                  )} />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-white">
                        Diagnostic Report
                      </span>
                      {currentStepData.severity && (
                        <span className={cn(
                          "text-[10px] font-bold px-2 py-0.5 rounded-full",
                          currentStepData.severity.includes('P0') && "text-red-400 bg-red-500/20 border border-red-500/30",
                          currentStepData.severity.includes('P1') && "text-orange-400 bg-orange-500/20 border border-orange-500/30",
                          currentStepData.severity.includes('P2') && "text-yellow-400 bg-yellow-500/20 border border-yellow-500/30",
                          currentStepData.severity.includes('P3') && "text-blue-400 bg-blue-500/20 border border-blue-500/30"
                        )}>
                          {currentStepData.severity.split(' - ')[0]}
                        </span>
                      )}
                    </div>
                    {currentStepData.responsible_team && (
                      <div className="flex items-center gap-1.5 mt-1">
                        <span className="text-[9px] text-zinc-500">Assigned to</span>
                        <span className="text-[10px] font-semibold text-emerald-400">
                          {currentStepData.responsible_team} Team
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                {currentStepData.alert_sent && (
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-500/15 border border-red-500/40"
                  >
                    <Zap className="w-3 h-3 text-red-400 animate-pulse" />
                    <span className="text-[9px] font-bold uppercase tracking-wider text-red-400">
                      Alert Sent
                    </span>
                  </motion.div>
                )}
              </div>

              {/* Main Diagnosis */}
              {currentStepData.diagnosis && (
                <div className="mb-3">
                  <p className="text-sm text-zinc-200 leading-relaxed font-medium">
                    {currentStepData.diagnosis}
                  </p>
                </div>
              )}

              {/* Metrics Summary - Compact */}
              <div className="grid grid-cols-3 gap-2 mb-3 pb-3 border-b border-white/5">
                {currentStepData.f_score !== undefined && (
                  <div className="bg-zinc-900/50 rounded-lg p-2">
                    <div className="flex items-center gap-1 mb-1">
                      <Zap className="w-3 h-3 text-amber-400" />
                      <span className="text-[8px] uppercase tracking-wider text-zinc-500">F-Score</span>
                    </div>
                    <span className="text-lg font-bold font-mono text-amber-400">
                      {currentStepData.f_score}
                    </span>
                    <span className="text-xs text-zinc-600">/100</span>
                  </div>
                )}
                
                {currentStepData.confusion_score !== undefined && (
                  <div className="bg-zinc-900/50 rounded-lg p-2">
                    <div className="flex items-center gap-1 mb-1">
                      <Activity className={cn(
                        "w-3 h-3",
                        currentStepData.confusion_score >= 7 ? "text-red-400" :
                        currentStepData.confusion_score >= 4 ? "text-yellow-400" :
                        "text-emerald-400"
                      )} />
                      <span className="text-[8px] uppercase tracking-wider text-zinc-500">Confusion</span>
                    </div>
                    <span className={cn(
                      "text-lg font-bold font-mono",
                      currentStepData.confusion_score >= 7 ? "text-red-400" :
                      currentStepData.confusion_score >= 4 ? "text-yellow-400" :
                      "text-emerald-400"
                    )}>
                      {currentStepData.confusion_score}
                    </span>
                    <span className="text-xs text-zinc-600">/10</span>
                  </div>
                )}
                
                {currentStepData.dwell_time_ms !== undefined && currentStepData.dwell_time_ms > 0 && (
                  <div className="bg-zinc-900/50 rounded-lg p-2">
                    <div className="flex items-center gap-1 mb-1">
                      <Activity className="w-3 h-3 text-purple-400" />
                      <span className="text-[8px] uppercase tracking-wider text-zinc-500">Duration</span>
                    </div>
                    <span className="text-lg font-bold font-mono text-purple-400">
                      {(currentStepData.dwell_time_ms / 1000).toFixed(1)}
                    </span>
                    <span className="text-xs text-zinc-600">s</span>
                  </div>
                )}
              </div>

              {/* Evidence Section */}
              <div className="space-y-2">
                {/* Network Evidence */}
                {currentStepData.network_logs && currentStepData.network_logs.length > 0 && (
                  <div className="bg-zinc-900/30 rounded-lg p-2.5">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <Network className="w-3.5 h-3.5 text-blue-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
                        Network Evidence
                      </span>
                    </div>
                    <div className="space-y-1 font-mono">
                      {currentStepData.network_logs.slice(0, 3).map((log: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-[10px]">
                          <span className={cn(
                            "font-bold w-9 text-center rounded px-1",
                            log.status >= 500 ? "text-red-400 bg-red-500/10" :
                            log.status >= 400 ? "text-amber-400 bg-amber-500/10" :
                            "text-emerald-400 bg-emerald-500/10"
                          )}>
                            {log.status}
                          </span>
                          <span className="text-zinc-500 w-12">{log.method}</span>
                          <span className="text-zinc-400 truncate flex-1">{log.url}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Console Evidence */}
                {currentStepData.console_logs && currentStepData.console_logs.length > 0 && (
                  <div className="bg-zinc-900/30 rounded-lg p-2.5">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <Terminal className="w-3.5 h-3.5 text-yellow-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
                        Console Evidence
                      </span>
                    </div>
                    <div className="space-y-1 font-mono text-[9px]">
                      {currentStepData.console_logs.slice(0, 3).map((log: string, i: number) => (
                        <div key={i} className="text-zinc-400 leading-relaxed pl-2 border-l border-yellow-500/30">
                          {log}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* UX Issues */}
                {currentStepData.ux_issues && currentStepData.ux_issues.length > 0 && (
                  <div className="bg-zinc-900/30 rounded-lg p-2.5">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <Eye className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
                        UX Observations
                      </span>
                    </div>
                    <div className="space-y-1">
                      {currentStepData.ux_issues.slice(0, 3).map((issue: string, i: number) => (
                        <div key={i} className="flex items-start gap-2 text-[10px]">
                          <span className="text-cyan-500 mt-0.5">•</span>
                          <span className="text-zinc-400 leading-relaxed">{issue}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Show test results when complete */}
          {results && state === "complete" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 rounded-lg bg-zinc-800/50 border border-emerald-500/30"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-500" />
                  <span className="font-bold text-emerald-500">Test Complete</span>
                </div>
                <div className="text-xs text-zinc-400 space-y-1">
                  <div>Status: <span className="text-white">{results.status || 'N/A'}</span></div>
                  {results.passed !== undefined && (
                    <div>Passed: <span className="text-white">{results.passed}/{results.passed + results.failed}</span></div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {state === "analyzing" && (
            <motion.div 
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="flex items-center gap-2 text-emerald-500/40 pl-2"
            >
              <span className="">_</span>
              <span className="text-[10px] uppercase tracking-widest italic">Thinking...</span>
            </motion.div>
          )}
        </div>

        {/* Terminal Footer Info */}
        <div className="px-6 py-3 border-t border-white/5 bg-black/20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Persona: {persona}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Confidence: {state === "idle" ? "0%" : "94.2%"}</span>
            </div>
          </div>
          <span className="text-[9px] text-zinc-700 uppercase tracking-widest">Encrypted Stream v4.2</span>
        </div>
      </motion.div>
    </div>
  );
}
