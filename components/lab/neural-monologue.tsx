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
  currentAction?: string;
  maxSteps?: number;
}

export function NeuralMonologue({ state, step, persona, logs = [], results, currentStepData, currentAction, maxSteps = 5 }: NeuralMonologueProps) {
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
    <div className="flex flex-col gap-4" style={{ maxHeight: 'calc(100vh - 240px)' }}>
      {/* Steps Display - only show when test is running */}
      {state !== "idle" && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex gap-2 px-4"
        >
          {Array.from({ length: maxSteps }, (_, i) => i + 1).map((stepNum) => {
            const isPast = stepNum < step;
            const isCurrent = stepNum === step;
            const isComplete = state === "complete" && stepNum <= step;

            return (
              <div
                key={stepNum}
                className={cn(
                  "flex-1 h-1 rounded-full transition-all duration-300",
                  (isPast || isComplete) && "bg-emerald-500",
                  isCurrent && "bg-blue-500 animate-pulse",
                  stepNum > step && "bg-zinc-300 dark:bg-zinc-800"
                )}
              />
            );
          })}
        </motion.div>
      )}

      {/* Terminal Container */}
      <motion.div 
        initial={{ x: 50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="flex-1 rounded-2xl border border-zinc-200 dark:border-white/5 bg-zinc-100 dark:bg-zinc-900/30 backdrop-blur-xl overflow-hidden flex flex-col shadow-2xl transition-colors duration-300"
      >
        {/* Terminal Header */}
        <div className="px-6 py-4 border-b border-zinc-200 dark:border-white/5 flex items-center justify-between bg-zinc-200/50 dark:bg-white/5 transition-colors duration-300">
          <div className="flex items-center gap-3">
            <Terminal className="w-4 h-4 text-emerald-500" />
            <span className="font-mono text-xs uppercase text-zinc-600 dark:text-zinc-400 transition-colors duration-300">Test Output</span>
          </div>
        </div>

        {/* Terminal Body */}
        <div 
          ref={containerRef}
          className="flex-1 p-6 font-mono text-xs overflow-y-auto space-y-4"
          style={{
            maxHeight: 'calc(100vh - 340px)',
            scrollbarWidth: 'thin',
            scrollbarColor: '#4ade80 #18181b'
          }}
        >
          {state === "scanning" && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-500">
                <span>Initializing test...</span>
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
                  <div className="w-6 h-6 rounded-lg bg-zinc-200 dark:bg-zinc-800 flex items-center justify-center border border-zinc-300 dark:border-white/5 group-hover:scale-110 transition-transform text-emerald-500 dark:text-emerald-400 transition-colors duration-300">
                    <Terminal className="w-3 h-3" />
                  </div>
                </div>
                
                <div className="flex-1 space-y-1">
                  <p className="text-zinc-700 dark:text-zinc-300 leading-relaxed group-hover:text-zinc-900 dark:group-hover:text-white transition-colors text-xs">
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
              className="mt-4 p-4 rounded-xl bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800/80 dark:to-zinc-900/80 border border-emerald-500/30 shadow-2xl transition-colors duration-300"
            >
              {/* Header with Severity & Team */}
              <div className="flex items-start justify-between mb-3 pb-3 border-b border-zinc-300 dark:border-white/10 transition-colors duration-300">
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
                      <span className="text-xs font-bold uppercase tracking-wider text-zinc-900 dark:text-white transition-colors duration-300">
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
                      {/* Analysis status badge */}
                      {currentStepData.analysis_complete ? (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full text-emerald-400 bg-emerald-500/20 border border-emerald-500/30">
                          ✓ COMPLETE
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full text-amber-400 bg-amber-500/20 border border-amber-500/30 animate-pulse">
                          ⚙ ANALYZING
                        </span>
                      )}
                    </div>
                    {currentStepData.responsible_team && (
                      <div className="flex items-center gap-1.5 mt-1">
                        <span className="text-[9px] text-zinc-500 dark:text-zinc-500">Assigned to</span>
                        <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
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
                  <p className="text-sm text-zinc-800 dark:text-zinc-200 leading-relaxed font-medium transition-colors duration-300">
                    {currentStepData.diagnosis}
                  </p>
                </div>
              )}

              {/* Metrics Summary - Compact */}
              <div className="grid grid-cols-3 gap-2 mb-3 pb-3 border-b border-zinc-300 dark:border-white/5 transition-colors duration-300">
                {currentStepData.f_score !== undefined && (
                  <div className="bg-zinc-200 dark:bg-zinc-900/50 rounded-lg p-2 transition-colors duration-300">
                    <div className="flex items-center gap-1 mb-1">
                      <Zap className="w-3 h-3 text-amber-500 dark:text-amber-400" />
                      <span className="text-[8px] uppercase tracking-wider text-zinc-500 dark:text-zinc-500">F-Score</span>
                    </div>
                    <span className="text-lg font-bold font-mono text-amber-600 dark:text-amber-400">
                      {currentStepData.f_score}
                    </span>
                    <span className="text-xs text-zinc-500 dark:text-zinc-600">/100</span>
                  </div>
                )}
                
                {currentStepData.confusion_score !== undefined && (
                  <div className="bg-zinc-200 dark:bg-zinc-900/50 rounded-lg p-2 transition-colors duration-300">
                    <div className="flex items-center gap-1 mb-1">
                      <Activity className={cn(
                        "w-3 h-3",
                        currentStepData.confusion_score >= 7 ? "text-red-500 dark:text-red-400" :
                        currentStepData.confusion_score >= 4 ? "text-yellow-500 dark:text-yellow-400" :
                        "text-emerald-600 dark:text-emerald-400"
                      )} />
                      <span className="text-[8px] uppercase tracking-wider text-zinc-500 dark:text-zinc-500">Confusion</span>
                    </div>
                    <span className={cn(
                      "text-lg font-bold font-mono",
                      currentStepData.confusion_score >= 7 ? "text-red-600 dark:text-red-400" :
                      currentStepData.confusion_score >= 4 ? "text-yellow-600 dark:text-yellow-400" :
                      "text-emerald-600 dark:text-emerald-400"
                    )}>
                      {currentStepData.confusion_score}
                    </span>
                    <span className="text-xs text-zinc-500 dark:text-zinc-600">/10</span>
                  </div>
                )}
                
                {currentStepData.dwell_time_ms !== undefined && currentStepData.dwell_time_ms > 0 && (
                  <div className="bg-zinc-200 dark:bg-zinc-900/50 rounded-lg p-2 transition-colors duration-300">
                    <div className="flex items-center gap-1 mb-1">
                      <Activity className="w-3 h-3 text-purple-500 dark:text-purple-400" />
                      <span className="text-[8px] uppercase tracking-wider text-zinc-500 dark:text-zinc-500">Duration</span>
                    </div>
                    <span className="text-lg font-bold font-mono text-purple-600 dark:text-purple-400">
                      {(currentStepData.dwell_time_ms / 1000).toFixed(1)}
                    </span>
                    <span className="text-xs text-zinc-500 dark:text-zinc-600">s</span>
                  </div>
                )}
              </div>

              {/* Evidence Section */}
              <div className="space-y-2">
                {/* Network Evidence */}
                {currentStepData.network_logs && currentStepData.network_logs.length > 0 && (
                  <div className="bg-zinc-200 dark:bg-zinc-900/30 rounded-lg p-2.5 transition-colors duration-300">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <Network className="w-3.5 h-3.5 text-blue-500 dark:text-blue-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-700 dark:text-zinc-400 transition-colors duration-300">
                        Network Evidence
                      </span>
                    </div>
                    <div className="space-y-1 font-mono">
                      {currentStepData.network_logs.slice(0, 3).map((log: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-[10px]">
                          <span className={cn(
                            "font-bold w-9 text-center rounded px-1",
                            log.status >= 500 ? "text-red-500 dark:text-red-400 bg-red-500/10" :
                            log.status >= 400 ? "text-amber-500 dark:text-amber-400 bg-amber-500/10" :
                            "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10"
                          )}>
                            {log.status}
                          </span>
                          <span className="text-zinc-600 dark:text-zinc-500 w-12">{log.method}</span>
                          <span className="text-zinc-700 dark:text-zinc-400 truncate flex-1">{log.url}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Console Evidence */}
                {currentStepData.console_logs && currentStepData.console_logs.length > 0 && (
                  <div className="bg-zinc-200 dark:bg-zinc-900/30 rounded-lg p-2.5 transition-colors duration-300">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <Terminal className="w-3.5 h-3.5 text-yellow-500 dark:text-yellow-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-700 dark:text-zinc-400 transition-colors duration-300">
                        Console Evidence
                      </span>
                    </div>
                    <div className="space-y-1 font-mono text-[9px]">
                      {currentStepData.console_logs.slice(0, 3).map((log: string, i: number) => (
                        <div key={i} className="text-zinc-700 dark:text-zinc-400 leading-relaxed pl-2 border-l border-yellow-500/30 transition-colors duration-300">
                          {log}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* UX Issues */}
                {currentStepData.ux_issues && currentStepData.ux_issues.length > 0 && (
                  <div className="bg-zinc-200 dark:bg-zinc-900/30 rounded-lg p-2.5 transition-colors duration-300">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <Eye className="w-3.5 h-3.5 text-cyan-500 dark:text-cyan-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-700 dark:text-zinc-400 transition-colors duration-300">
                        UX Observations
                      </span>
                    </div>
                    <div className="space-y-1">
                      {currentStepData.ux_issues.slice(0, 3).map((issue: string, i: number) => (
                        <div key={i} className="flex items-start gap-2 text-[10px]">
                          <span className="text-cyan-600 dark:text-cyan-500 mt-0.5">•</span>
                          <span className="text-zinc-700 dark:text-zinc-400 leading-relaxed transition-colors duration-300">{issue}</span>
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
              className="mt-6 p-4 rounded-lg bg-zinc-200 dark:bg-zinc-800/50 border border-emerald-500/30 transition-colors duration-300"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-500" />
                  <span className="font-bold text-emerald-600 dark:text-emerald-500">Test Complete</span>
                </div>
                <div className="text-xs text-zinc-700 dark:text-zinc-400 space-y-1 transition-colors duration-300">
                  <div>Status: <span className="text-zinc-900 dark:text-white">{results.status || 'N/A'}</span></div>
                  {results.passed !== undefined && (
                    <div>Passed: <span className="text-zinc-900 dark:text-white">{results.passed}/{results.passed + results.failed}</span></div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </div>

      </motion.div>
    </div>
  );
}
