"use client";

import { cn } from "@/lib/utils";
import { AlertTriangle, Clock, Smartphone, Monitor, Brain, ChevronDown, Users, Gauge } from "lucide-react";
import { useState } from "react";

interface IncidentCardProps {
  title: string;
  description: string;
  severity: "P0" | "P1" | "P2" | "P3";
  timestamp: string;
  device: string;
  aiReasoning?: string;
  confusionTime?: number;
  impactEstimate?: string;
  responsibleTeam?: string;
  fScore?: number;
}

export function IncidentCard({ title, description, severity, timestamp, device, aiReasoning, confusionTime, impactEstimate, responsibleTeam, fScore }: IncidentCardProps) {
  const [showReasoning, setShowReasoning] = useState(false);
  
  const severityConfig = {
    P0: { 
      color: "from-red-500/20 to-red-600/20", 
      border: "border-red-500/30",
      text: "text-red-400",
      bg: "bg-red-500/10",
      glow: "shadow-red-500/20"
    },
    P1: { 
      color: "from-orange-500/20 to-orange-600/20", 
      border: "border-orange-500/30",
      text: "text-orange-400",
      bg: "bg-orange-500/10",
      glow: "shadow-orange-500/20"
    },
    P2: { 
      color: "from-yellow-500/20 to-yellow-600/20", 
      border: "border-yellow-500/30",
      text: "text-yellow-400",
      bg: "bg-yellow-500/10",
      glow: "shadow-yellow-500/20"
    },
    P3: { 
      color: "from-emerald-500/20 to-emerald-600/20", 
      border: "border-emerald-500/30",
      text: "text-emerald-400",
      bg: "bg-emerald-500/10",
      glow: "shadow-emerald-500/20"
    }
  };

  const config = severityConfig[severity];
  const isMobile = device.includes("iPhone") || device.includes("Samsung");

  return (
    <div className={cn(
      "group relative rounded-2xl border-2 backdrop-blur-sm p-6 transition-all duration-300 hover:scale-[1.02]",
      "bg-gradient-to-br from-white to-zinc-50 dark:from-zinc-900/60 dark:to-zinc-900/40 border-zinc-200 dark:border-white/10 hover:border-zinc-300 dark:hover:border-white/20",
      "hover:shadow-2xl"
    )}>
      {/* Severity badge */}
      <div className="flex items-start justify-between mb-4">
        <div className={cn(
          "px-3 py-1.5 rounded-lg text-xs font-bold border-2 flex items-center gap-2",
          config.border, config.text, config.bg
        )}>
          <AlertTriangle className="w-3 h-3" />
          {severity}
        </div>
        <div className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-500">
          <Clock className="w-3 h-3" />
          {timestamp}
        </div>
      </div>

      {/* Title */}
      <h3 className="text-base font-semibold text-zinc-900 dark:text-white mb-3 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
        {title}
      </h3>

      {/* Description */}
      <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed mb-4 transition-colors duration-300">
        {description}
      </p>

      {/* F-Score Meter */}
      {fScore !== undefined && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <Gauge className="w-3 h-3" />
              <span>Friction Score</span>
            </div>
            <span className={cn(
              "text-xs font-bold",
              fScore >= 70 ? "text-red-400" : fScore >= 50 ? "text-orange-400" : "text-emerald-400"
            )}>
              {fScore}/100
            </span>
          </div>
          <div className="w-full h-1.5 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden transition-colors duration-300">
            <div 
              className={cn(
                "h-full rounded-full transition-all duration-500",
                fScore >= 70 ? "bg-gradient-to-r from-red-500 to-red-600" : 
                fScore >= 50 ? "bg-gradient-to-r from-orange-500 to-orange-600" : 
                "bg-gradient-to-r from-emerald-500 to-emerald-600"
              )}
              style={{ width: `${fScore}%` }}
            />
          </div>
        </div>
      )}

      {/* AI Reasoning Section */}
      {aiReasoning && (
        <div className="mb-4">
          <button
            onClick={() => setShowReasoning(!showReasoning)}
            className="flex items-center gap-2 text-xs text-purple-400 hover:text-purple-300 transition-colors mb-2"
          >
            <Brain className="w-3 h-3" />
            <span>AI Analysis</span>
            <ChevronDown className={cn("w-3 h-3 transition-transform", showReasoning && "rotate-180")} />
          </button>
          {showReasoning && (
            <div className="rounded-lg bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 p-4 space-y-2">
              <p className="text-xs text-zinc-700 dark:text-zinc-300 leading-relaxed transition-colors duration-300">{aiReasoning}</p>
              {impactEstimate && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-zinc-500">Impact:</span>
                  <span className="text-orange-400 font-semibold">{impactEstimate}</span>
                </div>
              )}
              {confusionTime && confusionTime > 5 && (
                <div className="flex items-center gap-2 text-xs">
                  <Clock className="w-3 h-3 text-yellow-400" />
                  <span className="text-zinc-400">AI confusion detected: {confusionTime}s analyzing this issue</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 dark:bg-white/5 text-xs text-zinc-600 dark:text-zinc-400 transition-colors duration-300">
          {isMobile ? <Smartphone className="w-3 h-3" /> : <Monitor className="w-3 h-3" />}
          {device}
        </div>
        {responsibleTeam && (
          <div className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs",
            (responsibleTeam.toUpperCase() === "QA" || responsibleTeam.toUpperCase() === "BACKEND") 
              ? "bg-white/5 text-zinc-400"
              : (responsibleTeam.toUpperCase() === "FRONTEND")
              ? "bg-blue-500/10 border border-blue-500/20 text-blue-400"
              : "bg-purple-500/10 border border-purple-500/20 text-purple-400"
          )}>
            <Users className="w-3 h-3" />
            {responsibleTeam} Team
          </div>
        )}
      </div>

      {/* Hover glow effect */}
      <div className={cn(
        "absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10 blur-xl",
        config.color
      )} />
    </div>
  );
}
