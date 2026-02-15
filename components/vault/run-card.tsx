"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Clock, CheckCircle2, XCircle, AlertTriangle, Smartphone, Monitor, Image, Film, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface RunCardProps {
  run: any;
  onExpand: (runId: string) => void;
  isExpanded: boolean;
}

export function RunCard({ run, onExpand, isExpanded }: RunCardProps) {
  const incidentCount = run.incident_count || 0;
  const avgFScore = run.avg_f_score || 0;
  const stepCount = run.step_count || 0;
  
  // Calculate stats from incidents
  const passedSteps = Math.max(0, stepCount - incidentCount);
  const failedSteps = incidentCount;
  
  // Format timestamp
  let displayTime = "Unknown time";
  try {
    // Try ISO format first
    const date = new Date(run.timestamp);
    if (!isNaN(date.getTime())) {
      displayTime = date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } else {
      // Fallback to timestamp string
      displayTime = run.timestamp || run.id;
    }
  } catch (e) {
    displayTime = run.timestamp || run.id;
  }
  
  // Determine overall status
  const criticalIssues = run.severity_breakdown?.P0 || 0;
  const highIssues = run.severity_breakdown?.P1 || 0;
  
  const status = criticalIssues > 0 ? "critical" : highIssues > 0 ? "warning" : failedSteps > 0 ? "issues" : "passed";
  
  const statusConfig = {
    critical: { color: "bg-red-500/10 border-red-500/30", text: "text-red-400", icon: XCircle },
    warning: { color: "bg-orange-500/10 border-orange-500/30", text: "text-orange-400", icon: AlertTriangle },
    issues: { color: "bg-yellow-500/10 border-yellow-500/30", text: "text-yellow-400", icon: AlertTriangle },
    passed: { color: "bg-emerald-500/10 border-emerald-500/30", text: "text-emerald-400", icon: CheckCircle2 }
  };
  
  const config = statusConfig[status];
  const StatusIcon = config.icon;

  return (
    <div className={cn(
      "rounded-2xl border-2 backdrop-blur-sm transition-all duration-300",
      config.color,
      isExpanded ? "bg-zinc-100 dark:bg-zinc-900/60" : "bg-white dark:bg-zinc-900/40 hover:bg-zinc-50 dark:hover:bg-zinc-900/60"
    )}>
      {/* Run Header - Clickable */}
      <button
        onClick={() => onExpand(run.id)}
        className="w-full p-6 text-left flex items-start gap-4 group"
      >
        <div className={cn(
          "flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all",
          config.color
        )}>
          {isExpanded ? (
            <ChevronDown className="w-5 h-5 text-zinc-900 dark:text-white" />
          ) : (
            <ChevronRight className="w-5 h-5 text-zinc-900 dark:text-white group-hover:translate-x-0.5 transition-transform" />
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-3">
            <StatusIcon className={cn("w-5 h-5", config.text)} />
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-white transition-colors duration-300">
              Run #{run.id.slice(-6)}
            </h3>
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <Clock className="w-3 h-3" />
              {displayTime}
            </div>
          </div>
          
          {/* Issue Distribution */}
          {run.severity_breakdown && (
            <div className="mt-3 flex items-center gap-4">
              <span className="text-xs text-zinc-500">Issues:</span>
              <div className="flex items-center gap-3">
                {run.severity_breakdown.P0 > 0 && (
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-red-500/10 border border-red-500/30">
                    <div className="w-2 h-2 rounded-full bg-red-500" />
                    <span className="text-xs text-red-400 font-semibold">{run.severity_breakdown.P0} Critical</span>
                  </div>
                )}
                {run.severity_breakdown.P1 > 0 && (
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-orange-500/10 border border-orange-500/30">
                    <div className="w-2 h-2 rounded-full bg-orange-500" />
                    <span className="text-xs text-orange-400 font-semibold">{run.severity_breakdown.P1} High</span>
                  </div>
                )}
                {run.severity_breakdown.P2 > 0 && (
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-yellow-500/10 border border-yellow-500/30">
                    <div className="w-2 h-2 rounded-full bg-yellow-500" />
                    <span className="text-xs text-yellow-400 font-semibold">{run.severity_breakdown.P2} Medium</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </button>
      
      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-zinc-200 dark:border-white/10 transition-colors duration-300">
          {/* Metrics & GIF Preview */}
          <div className="px-6 pt-6 pb-4">
            <div className="grid grid-cols-2 gap-4">
              {/* Left: QA Metrics */}
              <div className="grid grid-cols-2 gap-3">
                {/* Tests Completed */}
                <div className="rounded-lg bg-zinc-100 dark:bg-white/5 p-3 border border-zinc-200 dark:border-white/10 transition-colors duration-300">
                  <div className="text-xs text-zinc-500 mb-1">Tests Completed</div>
                  <div className="text-2xl font-bold text-zinc-900 dark:text-white">{ stepCount}</div>
                </div>
                
                {/* Pass Rate */}
                <div className="rounded-lg bg-zinc-100 dark:bg-white/5 p-3 border border-zinc-200 dark:border-white/10 transition-colors duration-300">
                  <div className="text-xs text-zinc-500 mb-1">Pass</div>
                  <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{passedSteps}</div>
                </div>
                
                {/* Fail Count */}
                <div className="rounded-lg bg-zinc-100 dark:bg-white/5 p-3 border border-zinc-200 dark:border-white/10 transition-colors duration-300">
                  <div className="text-xs text-zinc-500 mb-1">Fail</div>
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">{failedSteps}</div>
                </div>
                
                {/* Friction Score */}
                <div className="rounded-lg bg-zinc-100 dark:bg-white/5 p-3 border border-zinc-200 dark:border-white/10 transition-colors duration-300">
                  <div className="text-xs text-zinc-500 mb-1">Friction Score</div>
                  <div className={cn(
                    "text-2xl font-bold",
                    avgFScore >= 60 ? "text-red-600 dark:text-red-400" : avgFScore >= 40 ? "text-orange-600 dark:text-orange-400" : "text-emerald-600 dark:text-emerald-400"
                  )}>
                    {avgFScore.toFixed(0)}
                  </div>
                </div>
              </div>

              {/* Right: GIF Preview */}
              <div className="rounded-xl bg-zinc-100 dark:bg-white/5 border border-zinc-200 dark:border-white/10 p-4 transition-colors duration-300">
                <h4 className="text-sm font-semibold text-zinc-900 dark:text-white mb-3 flex items-center gap-2 transition-colors duration-300">
                  <Film className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                  Test Replay
                </h4>
                {run.evidence_files && run.evidence_files.find((f: any) => f.type === 'gif') ? (
                  <div className="space-y-2">
                    {run.evidence_files
                      .filter((file: any) => file.type === 'gif')
                      .slice(0, 1)
                      .map((file: any, idx: number) => (
                        <div key={idx} className="rounded-lg overflow-hidden border border-zinc-300 dark:border-white/20 transition-colors duration-300">
                          <img
                            src={`http://localhost:8000/api/reports/${file.path}`}
                            alt="Test replay"
                            className="w-full h-auto max-h-80 object-contain"
                            loading="lazy"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              const parent = target.parentElement;
                              if (parent) {
                                const errorMsg = document.createElement('div');
                                errorMsg.className = 'text-xs text-zinc-500 p-4 text-center';
                                errorMsg.textContent = 'GIF not available';
                                parent.appendChild(errorMsg);
                              }
                            }}
                          />
                        </div>
                      ))
                    }
                  </div>
                ) : (
                  <div className="text-xs text-zinc-600 dark:text-zinc-600 py-8 text-center">
                    No GIF recordings available
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Issues List with Inline Evidence */}
          {run.incidents && run.incidents.length > 0 && (
            <div className="px-6 pb-6 space-y-4 border-t border-zinc-200 dark:border-white/10 pt-4 transition-colors duration-300">
          {run.incidents.map((incident: any, idx: number) => (
            <div
              key={incident.id || idx}
              className="rounded-lg bg-zinc-100 dark:bg-white/5 border border-zinc-200 dark:border-white/10 overflow-hidden hover:bg-zinc-200 dark:hover:bg-white/[0.07] transition-all"
            >
              {/* Issue Header - Always Visible */}
              <div className="p-3.5">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      "px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide",
                      incident.severity === "P0" ? "bg-red-500/20 text-red-400 border border-red-500/30" :
                      incident.severity === "P1" ? "bg-orange-500/20 text-orange-400 border border-orange-500/30" :
                      incident.severity === "P2" ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30" :
                      "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    )}>
                      {incident.severity}
                    </div>
                    <h4 className="text-sm font-semibold text-zinc-900 dark:text-white transition-colors duration-300">
                      Step {incident.step_id || idx + 1}: {incident.title || incident.action_taken || "Issue Detected"}
                    </h4>
                  </div>
                  <div className="flex items-center gap-2">
                    {incident.device && (
                      <div className="px-2 py-0.5 rounded bg-zinc-200 dark:bg-zinc-800/50 border border-zinc-300 dark:border-zinc-700/50 text-[11px] text-zinc-600 dark:text-zinc-400 font-medium transition-colors duration-300">
                        {incident.device}
                      </div>
                    )}
                  </div>
                </div>
                
                <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed mb-2.5 transition-colors duration-300">
                  {incident.description || incident.diagnosis || incident.monologue || "No details available"}
                </p>
                
                {/* Inline Screenshot Display */}
                {(incident.screenshot_before || incident.screenshot_after) && (
                  <div className="mt-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const btn = e.currentTarget;
                        const evidenceDiv = btn.nextElementSibling as HTMLElement;
                        if (evidenceDiv) {
                          evidenceDiv.style.display = evidenceDiv.style.display === 'none' ? 'flex' : 'none';
                          btn.textContent = evidenceDiv.style.display === 'none' ? '🔽 Show Evidence' : '🔼 Hide Evidence';
                        }
                      }}
                      className="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors"
                    >
                      🔽 Show Evidence
                    </button>
                    <div style={{display: 'none'}} className="flex gap-2">
                      {incident.screenshot_before && (
                        <div className="flex-1">
                          <div className="text-xs text-zinc-500 mb-1">Before</div>
                          <img 
                            src={`http://localhost:8000/api/reports/${run.id}/screenshots/${incident.screenshot_before.split('/').pop()}`}
                            alt="Before screenshot"
                            className="w-full h-72 object-contain rounded border border-zinc-300 dark:border-white/20 bg-zinc-50 dark:bg-black transition-colors duration-300"
                            loading="lazy"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              const parent = target.parentElement;
                              if (parent) {
                                const errorMsg = document.createElement('div');
                                errorMsg.className = 'text-xs text-red-400 p-2 bg-red-500/10 rounded border border-red-500/30';
                                errorMsg.textContent = 'Screenshot not available';
                                parent.appendChild(errorMsg);
                              }
                            }}
                          />
                        </div>
                      )}
                      {incident.screenshot_after && (
                        <div className="flex-1">
                          <div className="text-xs text-zinc-500 mb-1">After</div>
                          <img 
                            src={`http://localhost:8000/api/reports/${run.id}/screenshots/${incident.screenshot_after.split('/').pop()}`}
                            alt="After screenshot"
                            className="w-full h-72 object-contain rounded border border-zinc-300 dark:border-white/20 bg-zinc-50 dark:bg-black transition-colors duration-300"
                            loading="lazy"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              const parent = target.parentElement;
                              if (parent) {
                                const errorMsg = document.createElement('div');
                                errorMsg.className = 'text-xs text-red-400 p-2 bg-red-500/10 rounded border border-red-500/30';
                                errorMsg.textContent = 'Screenshot not available';
                                parent.appendChild(errorMsg);
                              }
                            }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {incident.f_score !== undefined && (
                  <div className="flex items-center gap-2 text-xs mt-3">
                    <span className="text-zinc-500">Friction:</span>
                    <div className="flex-1 max-w-[200px] h-2 rounded-full bg-zinc-200 dark:bg-white/10 overflow-hidden transition-colors duration-300">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          incident.f_score >= 60 ? "bg-red-500" :
                          incident.f_score >= 40 ? "bg-orange-500" :
                          "bg-emerald-500"
                        )}
                        style={{ width: `${incident.f_score}%` }}
                      />
                    </div>
                    <span className="font-mono text-zinc-600 dark:text-zinc-400 transition-colors duration-300">{incident.f_score.toFixed(0)}/100</span>
                  </div>
                )}
              </div>
            </div>
          ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
