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

          {/* Real-time Diagnostic Data */}
          {currentStepData && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-2 mt-3 p-3 rounded-lg bg-zinc-800/50 border border-emerald-500/20 max-h-[400px] overflow-y-auto scrollbar-hide"
            >
              {/* Confusion Score */}
              {currentStepData.confusion_score !== undefined && (
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <Activity className={cn(
                        "w-3 h-3",
                        currentStepData.confusion_score >= 7 ? "text-red-500" :
                        currentStepData.confusion_score >= 4 ? "text-amber-500" :
                        "text-emerald-500"
                      )} />
                      <span className="text-[9px] uppercase tracking-wider text-zinc-500">
                        Confusion
                      </span>
                    </div>
                    <span className={cn(
                      "text-xs font-bold font-mono",
                      currentStepData.confusion_score >= 7 ? "text-red-500" :
                      currentStepData.confusion_score >= 4 ? "text-amber-500" :
                      "text-emerald-500"
                    )}>
                      {currentStepData.confusion_score}/10
                    </span>
                  </div>
                  <div className="h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                    <div 
                      className={cn(
                        "h-full transition-all",
                        currentStepData.confusion_score >= 7 ? "bg-red-500" :
                        currentStepData.confusion_score >= 4 ? "bg-amber-500" :
                        "bg-emerald-500"
                      )}
                      style={{ width: `${(currentStepData.confusion_score / 10) * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Dwell Time */}
              {currentStepData.dwell_time_ms !== undefined && currentStepData.dwell_time_ms > 0 && (
                <div className="pt-2 border-t border-white/5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <Activity className="w-3 h-3 text-purple-500" />
                      <span className="text-[9px] uppercase tracking-wider text-zinc-500">
                        Duration
                      </span>
                    </div>
                    <span className="text-xs font-mono text-purple-400">
                      {(currentStepData.dwell_time_ms / 1000).toFixed(1)}s
                    </span>
                  </div>
                </div>
              )}

              {/* Network Logs */}
              {currentStepData.network_logs && currentStepData.network_logs.length > 0 && (
                <div className="pt-2 border-t border-white/5">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Network className="w-3 h-3 text-blue-500" />
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500">
                      Network
                    </span>
                  </div>
                  <div className="space-y-0.5 font-mono text-[9px]">
                    {currentStepData.network_logs.slice(0, 2).map((log: any, i: number) => (
                      <div key={i} className="flex items-center gap-1.5">
                        <span className={cn(
                          "font-bold w-8",
                          log.status >= 500 ? "text-red-500" :
                          log.status >= 400 ? "text-amber-500" :
                          "text-emerald-500"
                        )}>
                          {log.status}
                        </span>
                        <span className="text-zinc-600 w-10">{log.method}</span>
                        <span className="text-zinc-500 truncate flex-1 text-[8px]">{log.url}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Console Logs */}
              {currentStepData.console_logs && currentStepData.console_logs.length > 0 && (
                <div className="pt-2 border-t border-white/5">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Terminal className="w-3 h-3 text-yellow-500" />
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500">
                      Console
                    </span>
                  </div>
                  <div className="space-y-0.5 font-mono text-[8px]">
                    {currentStepData.console_logs.slice(0, 2).map((log: string, i: number) => (
                      <div key={i} className="text-zinc-400 truncate">{log}</div>
                    ))}
                  </div>
                </div>
              )}

              {/* F-Score if available */}
              {currentStepData.f_score !== undefined && (
                <div className="pt-2 border-t border-white/5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <Zap className="w-3 h-3 text-amber-500" />
                      <span className="text-[9px] uppercase tracking-wider text-zinc-500">
                        F-Score
                      </span>
                    </div>
                    <span className="text-xs font-bold font-mono text-amber-500">
                      {currentStepData.f_score}/100
                    </span>
                  </div>
                  <div className="h-1.5 bg-zinc-900 rounded-full overflow-hidden mt-1">
                    <div 
                      className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-red-500 transition-all"
                      style={{ width: `${currentStepData.f_score}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Diagnosis if failed */}
              {currentStepData.diagnosis && (
                <div className="pt-2 border-t border-white/5">
                  <div className="flex items-center gap-1.5 mb-1">
                    <AlertTriangle className="w-3 h-3 text-red-500" />
                    <span className="text-[9px] uppercase tracking-wider text-red-500">
                      Issue
                    </span>
                    {currentStepData.severity && (
                      <span className={cn(
                        "text-[8px] font-bold px-1.5 py-0.5 rounded ml-auto",
                        currentStepData.severity.includes('P0') && "text-red-500 bg-red-500/10",
                        currentStepData.severity.includes('P1') && "text-orange-500 bg-orange-500/10",
                        currentStepData.severity.includes('P2') && "text-yellow-500 bg-yellow-500/10",
                        currentStepData.severity.includes('P3') && "text-blue-500 bg-blue-500/10"
                      )}>
                        {currentStepData.severity.split(' - ')[0]}
                      </span>
                    )}
                  </div>
                  <p className="text-[9px] text-zinc-300 leading-relaxed">
                    {currentStepData.diagnosis}
                  </p>
                  <div className="flex items-center justify-between mt-1.5">
                    {currentStepData.responsible_team && (
                      <span className="text-[8px] text-zinc-600">
                        → <span className="text-emerald-500">{currentStepData.responsible_team}</span>
                      </span>
                    )}
                    {currentStepData.alert_sent && (
                      <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-red-500/10 border border-red-500/30"
                      >
                        <Zap className="w-2.5 h-2.5 text-red-400 animate-pulse" />
                        <span className="text-[7px] font-bold uppercase tracking-wider text-red-400">
                          Alert Sent
                        </span>
                      </motion.div>
                    )}
                  </div>
                </div>
              )}

              {/* UX Issues */}
              {currentStepData.ux_issues && currentStepData.ux_issues.length > 0 && (
                <div className="pt-2 border-t border-white/5">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Eye className="w-3 h-3 text-cyan-500" />
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500">
                      UX Issues
                    </span>
                  </div>
                  <div className="space-y-0.5">
                    {currentStepData.ux_issues.slice(0, 2).map((issue: string, i: number) => (
                      <div key={i} className="text-[8px] text-zinc-400 leading-relaxed">
                        • {issue}
                      </div>
                    ))}
                  </div>
                </div>
              )}
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
