"use client";

import { IncidentCard } from "@/components/vault/incident-card";
import { EvidencePreview } from "@/components/vault/evidence-preview";
import { AlertCircle } from "lucide-react";

interface IncidentGridProps {
  activeFilter: string;
  incidents?: any[];
  isLoading?: boolean;
}

export function IncidentGrid({ activeFilter, incidents = [], isLoading = false }: IncidentGridProps) {
  // Helper function to generate a concise title from diagnosis
  const generateTitle = (diagnosis: string | null, actionTaken: string | null): string => {
    if (!diagnosis && !actionTaken) return "Unknown Issue";
    
    const text = diagnosis || actionTaken || "";
    
    // Extract first sentence or clause
    const firstSentence = text.split(/[.!?;]/)[0].trim();
    
    // If it's still too long, truncate intelligently
    if (firstSentence.length > 80) {
      const words = firstSentence.split(' ');
      let title = '';
      for (const word of words) {
        if ((title + ' ' + word).length > 80) break;
        title += (title ? ' ' : '') + word;
      }
      return title + '...';
    }
    
    return firstSentence || "Issue Detected";
  };

  // Filter and map backend incidents to component format
  const mappedIncidents = incidents
    .filter((inc: any) => {
      // Additional frontend filter for quality
      const hasRealContent = (
        (inc.title && inc.title.length > 5) ||
        (inc.console_logs && inc.console_logs.length > 0) ||
        (inc.ux_issues && inc.ux_issues.length > 0) ||
        inc.f_score >= 60
      );
      return hasRealContent;
    })
    .map((inc: any) => {
      const diagnosis = inc.title && inc.title !== "Unknown Issue" ? inc.title : null;
      const actionTaken = inc.action_taken || null;
      const hasConsoleErrors = inc.console_logs && inc.console_logs.length > 0;
      
      // Generate description from available data
      let description = diagnosis || actionTaken || "";
      if (!description && hasConsoleErrors) {
        description = `Console errors detected: ${inc.console_logs.slice(0, 2).join(' ')}`;
      }
      
      return {
        id: inc.id || inc.test_id || inc.step_id || Math.random().toString(),
        title: generateTitle(diagnosis, actionTaken),
        description: description || "Issue detected during test execution",
        severity: inc.severity || "P3",
        timestamp: inc.timestamp || "Unknown time",
        device: inc.device || "Unknown Device",
        screenshot: inc.screenshot_after || inc.screenshot_before || null,
        gifPath: inc.gif_path || null,
        heatmapPath: inc.heatmap_path || null,
        aiReasoning: diagnosis || (hasConsoleErrors ? `Console errors: ${inc.console_logs.join(', ')}` : null),
        confusionTime: inc.confusion_score || (inc.dwell_time_ms ? inc.dwell_time_ms / 1000 : null),
        impactEstimate: inc.revenueLoss ? `Est. $${inc.revenueLoss.toLocaleString()} revenue impact` : null,
        responsibleTeam: inc.responsible_team || null,
        fScore: inc.f_score || null
      };
    });
  
  const filteredIncidents = mappedIncidents.filter(incident => {
    if (activeFilter === "all") return true;
    if (activeFilter === "mobile") return incident.device.includes("iPhone") || incident.device.includes("Samsung");
    if (activeFilter === "desktop") return incident.device === "Desktop";
    return incident.severity.toLowerCase() === activeFilter;
  });

  // Empty state
  if (!isLoading && filteredIncidents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="w-16 h-16 text-zinc-300 dark:text-zinc-700 mb-4" />
        <h3 className="text-xl font-semibold text-zinc-600 dark:text-zinc-400 mb-2">No Incidents Found</h3>
        <p className="text-sm text-zinc-500 dark:text-zinc-600 max-w-md">
          {activeFilter === "all" 
            ? "Run a test from the Lab to start detecting issues"
            : `No ${activeFilter} incidents found. Try a different filter.`
          }
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filteredIncidents.map((incident) => (
        <div key={incident.id} className="space-y-3">
          <IncidentCard 
            {...incident}
            aiReasoning={incident.aiReasoning ?? undefined}
            confusionTime={incident.confusionTime ?? undefined}
            impactEstimate={incident.impactEstimate ?? undefined}
            responsibleTeam={incident.responsibleTeam ?? undefined}
            fScore={incident.fScore ?? undefined}
          />
          <EvidencePreview 
            testId={incident.id}
            screenshot={incident.screenshot}
            gifPath={incident.gifPath}
            heatmapPath={incident.heatmapPath}
          />
        </div>
      ))}
    </div>
  );
}
