"use client";

import { useState } from "react";
import { Film, Image as ImageIcon, Thermometer, ChevronDown } from "lucide-react";

interface EvidencePreviewProps {
  screenshot?: string;
  testId?: string;
  gifPath?: string;
  heatmapPath?: string;
}

export function EvidencePreview({ screenshot, testId, gifPath, heatmapPath }: EvidencePreviewProps) {
  const [isExpanded, setIsExpanded] = useState(false); // Collapsed by default
  
  // Convert file paths to API URLs
  const getImageUrl = (path: string | undefined) => {
    if (!path) return null;
    const relativePath = path.includes('reports/') 
      ? path.split('reports/')[1] 
      : path.split('/').slice(-3).join('/');
    return `http://localhost:8000/api/reports/${relativePath}`;
  };

  const screenshotUrl = getImageUrl(screenshot);
  const gifUrl = getImageUrl(gifPath);
  const heatmapUrl = getImageUrl(heatmapPath);

  const hasEvidence = screenshot || gifPath || heatmapPath;
  const evidenceCount = [screenshot, gifPath, heatmapPath].filter(Boolean).length;

  if (!hasEvidence) {
    return (
      <div className="rounded-lg border border-white/10 bg-zinc-950/60 p-3 aspect-video flex items-center justify-center">
        <div className="text-center">
          <p className="text-xs text-zinc-500">No evidence available</p>
          {testId && <p className="text-[10px] text-zinc-600 mt-1">{testId}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/10 bg-zinc-950/60 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2 bg-zinc-900/60 hover:bg-zinc-900/80 transition-colors border-b border-white/10"
      >
        <span className="text-xs text-zinc-400 font-medium">
          Evidence ({evidenceCount} item{evidenceCount > 1 ? 's' : ''})
        </span>
        <ChevronDown className={`w-4 h-4 text-zinc-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
      </button>

      {/* Expanded View - Show all evidence when clicked */}
      {isExpanded && (
        <div className="p-3 space-y-3 bg-zinc-950/40">
          {screenshotUrl && (
            <div className="space-y-1">
              <div className="flex items-center gap-2 px-2">
                <ImageIcon className="w-3 h-3 text-emerald-400" />
                <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold">Screenshot</span>
              </div>
              <div className="rounded-lg overflow-hidden border border-white/10 bg-black/20 aspect-video">
                <img 
                  src={screenshotUrl} 
                  alt="Screenshot evidence" 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}
          
          {gifUrl && (
            <div className="space-y-1">
              <div className="flex items-center gap-2 px-2">
                <Film className="w-3 h-3 text-purple-400" />
                <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold">GIF Replay</span>
              </div>
              <div className="rounded-lg overflow-hidden border border-white/10 bg-black/20 aspect-video">
                <img 
                  src={gifUrl} 
                  alt="GIF replay" 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}
          
          {heatmapUrl && (
            <div className="space-y-1">
              <div className="flex items-center gap-2 px-2">
                <Thermometer className="w-3 h-3 text-orange-400" />
                <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold">Heatmap</span>
              </div>
              <div className="rounded-lg overflow-hidden border border-white/10 bg-black/20 aspect-video">
                <img 
                  src={heatmapUrl} 
                  alt="Interaction heatmap" 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
